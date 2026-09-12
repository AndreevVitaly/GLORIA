"""Manage an isolated development PostgreSQL cluster; never installs a Windows service."""

import argparse
import os
import subprocess
from pathlib import Path

import psycopg
from dotenv import dotenv_values
from psycopg import sql

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / ".local"
BIN = LOCAL / "pgsql" / "bin"
DATA = LOCAL / "pgdata"
CONFIG = dotenv_values(ROOT / ".env")


def run(program, *args, check=True):
    return subprocess.run(
        [str(BIN / f"{program}.exe"), *map(str, args)],
        check=check,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "start", "stop", "status", "create-db"])
    action = parser.parse_args().action
    if not (BIN / "pg_ctl.exe").exists():
        parser.error("Extract PostgreSQL Windows binaries into .local/pgsql first (see README).")
    if action == "init":
        if DATA.exists():
            parser.error("Cluster directory already exists; use start. No files were overwritten.")
        password_file = LOCAL / "init-password"
        try:
            password_file.write_text(CONFIG["POSTGRES_PASSWORD"], encoding="utf-8")
            run(
                "initdb",
                "-D",
                DATA,
                "-U",
                CONFIG["POSTGRES_USER"],
                "--pwfile",
                password_file,
                "--auth=scram-sha-256",
                "--encoding=UTF8",
                "--locale=C",
            )
        finally:
            password_file.unlink(missing_ok=True)
        with (DATA / "postgresql.conf").open("a", encoding="utf-8") as file:
            file.write("\nlisten_addresses = '127.0.0.1'\n")
            file.write(f"port = {int(CONFIG.get('POSTGRES_PORT', '5432'))}\n")
        run("pg_ctl", "-D", DATA, "-l", LOCAL / "postgres.log", "-w", "start")
        create_database()
    elif action == "create-db":
        create_database()
    elif action == "start":
        run("pg_ctl", "-D", DATA, "-l", LOCAL / "postgres.log", "-w", "start")
    elif action == "stop":
        run("pg_ctl", "-D", DATA, "-m", "fast", "-w", "stop")
    else:
        raise SystemExit(run("pg_ctl", "-D", DATA, "status", check=False).returncode)


def create_database():
    with psycopg.connect(
        host="127.0.0.1",
        port=CONFIG.get("POSTGRES_PORT", "5432"),
        user=CONFIG["POSTGRES_USER"],
        password=CONFIG["POSTGRES_PASSWORD"],
        dbname="postgres",
        autocommit=True,
    ) as connection:
        if not connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (CONFIG["POSTGRES_DB"],)
        ).fetchone():
            connection.execute(
                sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(
                    sql.Identifier(CONFIG["POSTGRES_DB"])
                )
            )
    print("Development database ready.")


if __name__ == "__main__":
    main()
