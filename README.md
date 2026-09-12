# GIOIA — этап 1

Фундамент интернет-магазина цветов. Проект находится в каталоге `GLORIA`, название продукта — **GIOIA**.
Реализован первый этап из технического задания. По отдельному запросу добавлена
[главная страница с демонстрационной коллекцией](docs/homepage.md).
Также добавлен [личный кабинет с разделом «Окружение»](docs/customer-account.md).
Интерфейс [Django Admin переведён на русский язык](docs/admin-russian.md).
Конструктор композиции, SVG-рендер, корзина, заказы и интеграции относятся к следующим этапам.
Исходное задание сохранено в [docs/specification.md](docs/specification.md).

Стек: Python 3.13, Django 5.2, PostgreSQL 17, Django Templates, Django REST Framework, pytest.
Точные версии зависимостей зафиксированы в `requirements.txt`; диапазоны — в `requirements.in`.
Django 5.2 поддерживает Python 3.13: [документация Django](https://docs.djangoproject.com/en/5.2/releases/5.2/).

## Структура

```text
GLORIA/
├── config/                   # настройки, URL, ASGI, WSGI
├── apps/
│   ├── accounts/             # пользователи, роли, разрешения, профили, адреса
│   ├── catalog/              # цветы, сорта, цвета, варианты, зелень, упаковка
│   ├── bouquet_builder/      # сохранённый букет, состав, пересчёт итогов в Admin
│   │   └── services/         # бизнес-логика вне views/templates
│   ├── core/                # абстрактные модели с временными метками
│   ├── cart/                # далее — каркасы Django-приложений, без бизнес-логики
│   ├── orders/
│   ├── payments/
│   ├── delivery/
│   ├── inventory/
│   ├── promotions/
│   ├── operator_panel/
│   ├── dashboard/
│   ├── content/
│   └── notifications/
├── tests/                   # тесты на настоящей PostgreSQL
├── scripts/local_postgres.py # управление переносимой PostgreSQL на Windows
├── compose.yaml             # альтернативный запуск PostgreSQL через Docker
├── manage.py
├── requirements.txt
└── .env.example
```

## Модели и таблицы

| Приложение | Модель | Таблица |
|---|---|---|
| accounts | User (AbstractUser) | users |
| accounts | Role | roles |
| accounts | UserRole | user_roles |
| accounts | CustomerProfile | customer_profiles |
| accounts | CustomerAddress | customer_addresses |
| catalog | FlowerType | flower_types |
| catalog | FlowerVariety | flower_varieties |
| catalog | FlowerColor | flower_colors |
| catalog | FlowerVariant | flower_variants |
| catalog | GreeneryType | greenery_types |
| catalog | PackagingType | packaging_types |
| bouquet_builder | CustomBouquet | custom_bouquets |
| bouquet_builder | CustomBouquetFlower | custom_bouquet_flowers |
| bouquet_builder | CustomBouquetGreenery | custom_bouquet_greenery |

Все предметные модели имеют явный `db_table`. Разрешения ролей связаны с Django Permission
через `role_permissions`; стандартные технические таблицы Django сохраняют стандартные имена.

Деньги — `Decimal`, количество компонентов строго положительное, цены неотрицательные.
Уникальны SKU, email без учёта регистра, назначение роли, компонент внутри букета и адрес
по умолчанию для одного пользователя. База проверяет сумму полей итоговой цены букета.
Согласованность сорта и вида проверяется при сохранении `FlowerVariant`.
Не используйте `QuerySet.update()`/`bulk_create()` для изменения этих связей: они обходят `clean()`.

Букет хранит UUID, владельца (необязателен для будущего гостевого сценария), статус,
63-битный seed, JSON и SVG как данные. SVG в Admin выводится экранированным текстом.
Удаление владельца сохраняет букет; удаление букета удаляет его строки состава.
Используемые компоненты каталога защищены от удаления через `PROTECT`.

## Запуск в подготовленном рабочем каталоге (PowerShell)

`.venv`, случайные локальные секреты в `.env` и переносимый кластер `.local/pgdata`
подготовлены при разработке. Они исключены из Git. PostgreSQL слушает только `127.0.0.1:5432`.
Системная служба не устанавливается.

```powershell
.\.venv\Scripts\python scripts\local_postgres.py status
# Если сервер остановлен:
.\.venv\Scripts\python scripts\local_postgres.py start
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

Admin: http://127.0.0.1:8000/admin/ — вход по email и паролю созданного суперпользователя.
Проверка процесса: http://127.0.0.1:8000/health/ (не проверяет соединение с базой).
Главная страница: http://127.0.0.1:8000/ — демонстрационная коллекция с поиском и фильтрами.
Учётная запись с заранее известным паролем не создаётся.

Остановка PostgreSQL:

```powershell
.\.venv\Scripts\python scripts\local_postgres.py stop
```

## Установка в новом окружении

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Задайте случайные `DJANGO_SECRET_KEY` и `POSTGRES_PASSWORD` в `.env`.
Для Docker выполните `docker compose up -d db`, затем миграции и запуск из раздела выше.
Либо подключите существующую PostgreSQL через параметры `POSTGRES_*`.
Тестовому пользователю базы нужно право `CREATEDB`: pytest создаёт и удаляет `test_gioia`.
Развёртывание в production требует отдельной роли базы с минимальными правами;
локальный кластер и Docker предназначены для разработки.

Вариант без Docker на Windows: скачайте
[официальные переносимые бинарные файлы PostgreSQL](https://www.postgresql.org/download/windows/)
и распакуйте `pgsql/bin`, `pgsql/lib`, `pgsql/share` в `.local/pgsql`.
Для этой рабочей копии использована сборка EDB PostgreSQL 17.11-3.
Выполните `python scripts/local_postgres.py init` через Python из `.venv`.
Повторная инициализация существующего каталога запрещена скриптом.
Если создание кластера прошло, а запуск прервался, выполните `start`, затем `create-db`.

## Доступ и Django Admin

Миграция создаёт три роли: `customer`, `operator`, `admin`. Пользователь может иметь несколько ролей.
`Role.permissions` назначаются явно суперпользователем; первоначально роли не дают разрешений.
Backend объединяет разрешения ролей со стандартными разрешениями Django. Название роли
не даёт автоматического обхода проверок. Неактивные пользователи не могут войти или получить права.
Для входа в Django Admin дополнительно нужен `is_staff=True`.

Управление пользователями, назначениями ролей и разрешениями ролей в Django Admin доступно
только суперпользователю — даже если сотруднику ошибочно выдали `change_user`.
Отдельные `/operator/` и `/management/` будут созданы на следующих этапах.
На первом этапе работа руководителя выполняется через суперпользователя Django Admin.

Все 14 моделей доступны в Admin: строки цветов и зелени — внутри карточки букета.
При сохранении строк их цены берутся из каталога на сервере, итоги пересчитываются сервисом
в транзакции. Поля итогов и цен строк недоступны для ручного редактирования.
Изменение цен каталога не переписывает уже сохранённые цены компонентов.
Упаковка пока существует как справочник: связь с букетом, ленты и дополнения — следующие этапы.
Для прямой работы с ORM после изменения состава вызовите `refresh_component_totals(bouquet)`
в той же транзакции. Модельные `save()` сами не пересчитывают суммы по связанным строкам.

Действия в Admin записываются стандартным `django_admin_log`. Предметный `audit_log` для будущих
рабочих интерфейсов ещё не реализован. Восстановление пароля по почте
и пользовательское API относятся к последующим этапам. DRF подключён с закрытыми
по умолчанию permissions; публичных API-маршрутов пока нет.

## Миграции и проверки

Созданы миграции:

- `apps/accounts/migrations/0001_initial.py` — пользователь, роли, профили, адреса;
- `apps/accounts/migrations/0002_seed_roles.py` — начальные роли;
- `apps/catalog/migrations/0001_initial.py` — справочники компонентов;
- `apps/bouquet_builder/migrations/0001_initial.py` — букет и состав.

```powershell
.\.venv\Scripts\python manage.py check
.\.venv\Scripts\python manage.py makemigrations --check --dry-run
.\.venv\Scripts\python manage.py showmigrations accounts catalog bouquet_builder
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
```

Тесты используют PostgreSQL из `.env`, без подмены SQLite. Проверяются модели, ограничения БД,
пароли и вход по email, роли, ограничения Admin, сохранение JSON/seed, цены состава,
удаление связанных объектов и серверный пересчёт при попытке подменить цену в форме Admin.
Воспроизводимость **алгоритма композиции** будет проверяться на этапе 2, когда появится composer.

Для production нужны собственные настройки HTTPS, почты, доменов, резервного копирования
и сервера приложений. `DJANGO_DEBUG=0` включает secure cookies и HTTPS redirect;
это фундамент разработки, а не готовое production-развёртывание магазина.
