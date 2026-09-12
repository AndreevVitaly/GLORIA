from datetime import timedelta
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.accounts.models import CustomerConnection, CustomerProfile, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def customer_client(client, user):
    client.force_login(user)
    return client


def profile_data(user, **values):
    return {
        "email": user.email,
        "first_name": "Анна",
        "phone": "+79991234567",
        "birth_date": "1992-04-15",
        "gender": "female",
        **values,
    }


def photo_file():
    stream = BytesIO()
    Image.new("RGB", (64, 96), "pink").save(stream, format="PNG")
    return SimpleUploadedFile("photo.png", stream.getvalue(), content_type="image/png")


@pytest.mark.parametrize(
    "url", ["/account/", "/account/environment/", "/account/avatar/", "/account/password/"]
)
def test_guest_redirect_to_customer_login(client, url):
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith("/account/login/?next=")


def test_public_signup_and_login(client):
    response = client.post(
        reverse("accounts:signup"),
        {
            "first_name": "Анна",
            "email": "NEW@example.com",
            "phone": "+79991234567",
            "password1": "Unique-example-password-385!",
            "password2": "Unique-example-password-385!",
            "is_staff": "true",
            "is_superuser": "true",
            "roles": "admin",
        },
    )
    assert response.status_code == 302
    user = User.objects.get(email="new@example.com")
    assert not user.is_staff and not user.is_superuser
    assert user.roles.get().code == Role.Code.CUSTOMER
    assert user.customer_profile
    assert client.get("/account/").status_code == 200
    assert client.get("/account/logout/").status_code == 405
    assert client.post("/account/logout/").status_code == 302
    assert client.get("/account/").status_code == 302
    assert (
        client.post(
            "/account/login/",
            {
                "username": "NEW@example.com",
                "password": "Unique-example-password-385!",
                "next": "https://attacker.example/",
            },
        ).url
        == "/account/"
    )


def test_signup_duplicate_email_and_weak_password(client, user):
    response = client.post(
        "/account/signup/",
        {
            "email": "CUSTOMER@example.com",
            "password1": "123",
            "password2": "123",
        },
    )
    assert response.status_code == 200
    assert "email" in response.context["form"].errors
    assert "password2" in response.context["form"].errors
    assert User.objects.count() == 1


def test_profile_persists_and_cannot_set_privileged_fields(customer_client, user):
    response = customer_client.post(
        "/account/",
        profile_data(
            user, is_staff="true", is_superuser="true", notes="injected", marketing_consent="on"
        ),
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.first_name == "Анна"
    assert user.phone == "+79991234567"
    assert not user.is_staff and not user.is_superuser
    profile = user.customer_profile
    assert str(profile.birth_date) == "1992-04-15"
    assert profile.gender == "female"
    assert profile.notes == "" and profile.marketing_consent is False
    assert customer_client.get("/account/").context["account_form"].initial["first_name"] == "Анна"


def test_email_change_requires_password(customer_client, user):
    response = customer_client.post("/account/", profile_data(user, email="new@example.com"))
    assert response.status_code == 200
    assert "current_password" in response.context["account_form"].errors
    user.refresh_from_db()
    assert user.email == "customer@example.com"
    response = customer_client.post(
        "/account/",
        profile_data(user, email="new@example.com", current_password="Long-test-password-42"),
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.email == "new@example.com"
    assert customer_client.get("/account/").status_code == 200


def test_duplicate_email_edit(customer_client, user):
    User.objects.create_user(email="other@example.com")
    response = customer_client.post(
        "/account/",
        profile_data(user, email="OTHER@example.com", current_password="Long-test-password-42"),
    )
    assert response.status_code == 200
    assert "email" in response.context["account_form"].errors
    user.refresh_from_db()
    assert user.email == "customer@example.com"


@pytest.mark.parametrize(
    "values,error",
    [
        ({"birth_date": str(timezone.localdate() + timedelta(days=1))}, "birth_date"),
        ({"birth_date": "invalid"}, "birth_date"),
        ({"gender": "invalid"}, "gender"),
    ],
)
def test_invalid_profile_is_atomic(customer_client, user, values, error):
    response = customer_client.post("/account/", profile_data(user, **values))
    assert response.status_code == 200
    assert error in response.context["profile_form"].errors
    user.refresh_from_db()
    assert user.first_name == ""


def test_profile_optional_data_and_phone_validation(customer_client, user):
    response = customer_client.post("/account/", profile_data(user, phone="invalid"))
    assert "phone" in response.context["account_form"].errors
    assert (
        customer_client.post(
            "/account/", profile_data(user, phone="", birth_date="", gender="")
        ).status_code
        == 302
    )


def test_avatar_upload_private_serving_and_delete(
    customer_client, user, settings, tmp_path, django_capture_on_commit_callbacks
):
    settings.MEDIA_ROOT = tmp_path
    assert (
        customer_client.post("/account/", profile_data(user, photo=photo_file())).status_code == 302
    )
    profile = CustomerProfile.objects.get(user=user)
    old_name = profile.avatar.name
    assert old_name.endswith(".jpg")
    with Image.open(profile.avatar.path) as image:
        assert image.format == "JPEG" and image.size == (512, 512)
    response = customer_client.get("/account/avatar/")
    assert response.status_code == 200
    assert response["Cache-Control"] == "private, no-store"
    assert b"".join(response.streaming_content).startswith(b"\xff\xd8")
    other = User.objects.create_user(email="other@example.com")
    another_client = Client()
    another_client.force_login(other)
    assert another_client.get("/account/avatar/").status_code == 404
    assert another_client.get("/media/" + old_name).status_code == 404
    with django_capture_on_commit_callbacks(execute=True):
        assert (
            customer_client.post("/account/", profile_data(user, remove_photo="on")).status_code
            == 302
        )
    assert not (tmp_path / old_name).exists()
    profile.refresh_from_db()
    assert not profile.avatar
    assert customer_client.get("/account/avatar/").status_code == 404


@pytest.mark.parametrize(
    "content,mime,name",
    [
        (b"<svg onload=alert(1)></svg>", "image/svg+xml", "photo.svg"),
        (b"not an image", "image/jpeg", "photo.jpg"),
        (b"x" * (5 * 1024 * 1024 + 1), "image/png", "huge.png"),
    ],
    ids=["svg", "invalid-image", "oversized"],
)
def test_invalid_avatar_rejected(customer_client, user, settings, tmp_path, content, mime, name):
    settings.MEDIA_ROOT = tmp_path
    response = customer_client.post(
        "/account/", profile_data(user, photo=SimpleUploadedFile(name, content, content_type=mime))
    )
    assert response.status_code == 200
    assert "photo" in response.context["profile_form"].errors
    assert not CustomerProfile.objects.get(user=user).avatar


def test_avatar_mime_mismatch(customer_client, user, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    photo = photo_file()
    photo.content_type = "image/jpeg"
    response = customer_client.post("/account/", profile_data(user, photo=photo))
    assert "photo" in response.context["profile_form"].errors


def test_environment_crud_free_text_and_duplicate_labels(customer_client, user):
    for label in ["супруга", "тёща", "подруга Анна", "супруга"]:
        assert customer_client.post("/account/environment/", {"label": label}).status_code == 302
    assert user.environment.count() == 4
    connection = user.environment.first()
    assert (
        customer_client.post(
            reverse("accounts:connection_edit", args=[connection.pk]),
            {"label": "Моя лучшая подруга\nАнна"},
        ).status_code
        == 302
    )
    connection.refresh_from_db()
    assert connection.label == "Моя лучшая подруга\nАнна"
    url = reverse("accounts:connection_delete", args=[connection.pk])
    assert customer_client.get(url).status_code == 405
    assert customer_client.post(url).status_code == 302
    assert user.environment.count() == 3


def test_environment_ownership(customer_client, user):
    other = User.objects.create_user(email="other@example.com")
    connection = CustomerConnection.objects.create(user=other, label="Чужая запись")
    for action in ["connection_edit", "connection_delete"]:
        url = reverse("accounts:" + action, args=[connection.pk])
        assert customer_client.post(url, {"label": "Изменено", "user": user.pk}).status_code == 404
    response = customer_client.get("/account/environment/")
    assert "Чужая запись" not in response.content.decode()
    assert (
        customer_client.post(
            "/account/environment/",
            {
                "label": "Своя запись",
                "user": other.pk,
            },
        ).status_code
        == 302
    )
    assert user.environment.get().label == "Своя запись"
    connection.refresh_from_db()
    assert connection.label == "Чужая запись"


def test_environment_pagination_has_no_record_cap(customer_client, user):
    CustomerConnection.objects.bulk_create(
        [CustomerConnection(user=user, label=f"Человек {index}") for index in range(101)]
    )
    response = customer_client.get("/account/environment/?page=6")
    assert response.status_code == 200
    assert response.context["connections"].paginator.count == 101
    assert len(response.context["connections"]) == 1
    assert customer_client.post("/account/environment/", {"label": "Ещё один"}).status_code == 302
    assert user.environment.count() == 102


def test_empty_label_and_escaped_html(customer_client, user):
    response = customer_client.post("/account/environment/", {"label": "   "})
    assert response.status_code == 200
    assert response.context["connection_form"].errors
    customer_client.post("/account/environment/", {"label": '<script>alert("x")</script>'})
    response = customer_client.get("/account/environment/")
    assert '<script>alert("x")</script>' not in response.content.decode()
    assert "&lt;script&gt;" in response.content.decode()


def test_csrf_required(user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    connection = CustomerConnection.objects.create(user=user, label="Мама")
    for url in [
        "/account/",
        "/account/environment/",
        "/account/logout/",
        reverse("accounts:connection_delete", args=[connection.pk]),
    ]:
        assert client.post(url, {}).status_code == 403


def test_password_change_keeps_session(customer_client, user):
    response = customer_client.post(
        "/account/password/",
        {
            "old_password": "Long-test-password-42",
            "new_password1": "New-unique-password-468!",
            "new_password2": "New-unique-password-468!",
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("New-unique-password-468!")
    assert customer_client.get("/account/").status_code == 200
