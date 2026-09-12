import pytest
from django.contrib.auth.models import Permission

from apps.accounts.models import Role, User

pytestmark = pytest.mark.django_db


def test_guest_and_customer_admin_denied(client, user):
    assert client.get("/admin/").status_code == 302
    client.force_login(user)
    assert client.get("/admin/").status_code == 302


def test_operator_grants_do_not_allow_user_escalation(client, user):
    role = Role.objects.get(code=Role.Code.OPERATOR)
    role.permissions.add(
        *Permission.objects.filter(
            codename__in=[
                "view_flowervariant",
                "change_user",
                "view_user",
                "change_role",
                "view_role",
            ]
        )
    )
    user.roles.add(role)
    user.is_staff = True
    user.save()
    client.force_login(user)
    assert client.get("/admin/catalog/flowervariant/").status_code == 200
    assert client.get("/admin/accounts/user/").status_code == 403
    assert client.get("/admin/accounts/role/").status_code == 403
    assert client.get("/admin/catalog/flowervariant/add/").status_code == 403


@pytest.mark.parametrize(
    "path",
    [
        "/admin/",
        "/admin/accounts/user/",
        "/admin/accounts/user/add/",
        "/admin/accounts/role/",
        "/admin/accounts/userrole/",
        "/admin/accounts/customerprofile/",
        "/admin/accounts/customeraddress/",
        "/admin/catalog/flowertype/",
        "/admin/catalog/flowervariety/",
        "/admin/catalog/flowercolor/",
        "/admin/catalog/flowervariant/",
        "/admin/catalog/greenerytype/",
        "/admin/catalog/packagingtype/",
        "/admin/bouquet_builder/custombouquet/",
        "/admin/bouquet_builder/custombouquet/add/",
    ],
)
def test_superuser_admin_pages(client, path):
    admin = User.objects.create_superuser(email="admin@example.com", password="Strong-password-94")
    client.force_login(admin)
    assert client.get(path).status_code == 200


def test_health(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["project"] == "GIOIA"


def test_admin_uses_russian_labels(client):
    admin = User.objects.create_superuser(
        email="russian-admin@example.com", password="Strong-password-94"
    )
    client.force_login(admin)
    index = client.get("/admin/").content.decode()
    assert "Администрирование интернет-магазина" in index
    assert "Пользователи" in index
    assert "Каталог цветов" in index
    assert "Конструктор букетов" in index
    assert "Профили покупателей" in index
    assert "Адресаты" in index
    assert "Пользовательские букеты" in index

    form = client.get("/admin/catalog/flowervariant/add/").content.decode()
    for label in [
        "Вид цветка",
        "Сорт",
        "Цвет",
        "Артикул",
        "Длина стебля, см",
        "Закупочная цена",
        "Розничная цена",
        "Активно",
    ]:
        assert label in form
