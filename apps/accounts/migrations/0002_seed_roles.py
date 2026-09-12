from django.db import migrations


def seed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    for code, name in [
        ("customer", "Покупатель"),
        ("operator", "Оператор"),
        ("admin", "Руководитель"),
    ]:
        Role.objects.using(schema_editor.connection.alias).get_or_create(
            code=code, defaults={"name": name}
        )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    # Preserve roles on rollback: existing assignments must not be silently deleted.
    operations = [migrations.RunPython(seed_roles, migrations.RunPython.noop)]
