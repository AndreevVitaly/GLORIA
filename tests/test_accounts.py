import pytest
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.forms import GioiaUserCreationForm
from apps.accounts.models import CustomerAddress, CustomerProfile, Role, User, UserRole

pytestmark = pytest.mark.django_db


def test_user_password_and_email_login(user):
    assert user.email == "customer@example.com"
    assert user.password != "Long-test-password-42"
    assert user.check_password("Long-test-password-42")
    assert authenticate(username="CUSTOMER@example.com", password="Long-test-password-42") == user
    assert authenticate(email=user.email, password="wrong") is None
    assert user.uuid and user.created_at and user.updated_at


def test_inactive_user_cannot_login(user):
    user.is_active = False
    user.save()
    assert authenticate(email=user.email, password="Long-test-password-42") is None


def test_email_normalization_and_case_insensitive_uniqueness(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(email="CUSTOMER@example.com", username="second")
    other = User.objects.create_user(email=" Mixed@EXAMPLE.com ")
    assert other.email == "mixed@example.com"


def test_required_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="test")


def test_long_email_does_not_overflow_username():
    email = "a" * 64 + "@" + "b" * 60 + "." + "c" * 40 + ".com"
    user = User.objects.create_user(email=email, password="Long-test-password-42")
    user.full_clean()
    assert len(user.username) <= 150


def test_superuser_manager():
    user = User.objects.create_superuser(email="root@example.com", password="Strong-password-94")
    assert user.is_staff and user.is_superuser
    with pytest.raises(ValueError):
        User.objects.create_superuser(email="bad@example.com", is_staff=False)


def test_creation_form_hashes_password():
    form = GioiaUserCreationForm(
        data={
            "email": "form@example.com",
            "username": "form-user",
            "phone": "+79991234567",
            "password1": "Long-test-password-42",
            "password2": "Long-test-password-42",
        }
    )
    assert form.is_valid(), form.errors
    assert form.save().check_password("Long-test-password-42")


def test_seed_roles_and_multiple_assignments(user):
    assert set(Role.objects.values_list("code", flat=True)) == set(Role.Code.values)
    customer = Role.objects.get(code=Role.Code.CUSTOMER)
    operator = Role.objects.get(code=Role.Code.OPERATOR)
    UserRole.objects.create(user=user, role=customer)
    UserRole.objects.create(user=user, role=operator)
    assert user.roles.count() == 2
    with pytest.raises(IntegrityError), transaction.atomic():
        UserRole.objects.create(user=user, role=operator)


def test_role_permissions_and_inactive_restriction(user):
    operator = Role.objects.get(code=Role.Code.OPERATOR)
    operator.permissions.add(Permission.objects.get(codename="view_flowervariant"))
    user.roles.add(operator)
    assert user.has_perm("catalog.view_flowervariant")
    assert not user.has_perm("accounts.change_user")
    assert not user.has_perm("catalog.view_flowervariant", object())
    user.is_active = False
    user.save()
    user = User.objects.get(pk=user.pk)
    assert not user.has_perm("catalog.view_flowervariant")


def test_profile_and_multiple_addresses(user):
    profile = CustomerProfile.objects.create(user=user)
    assert profile.marketing_consent is False
    data = dict(
        user=user,
        title="Дом",
        recipient_name="Анна",
        recipient_phone="+79991234567",
        city="Москва",
        street="Цветочная",
        house="1",
    )
    CustomerAddress.objects.create(**data, is_default=True)
    CustomerAddress.objects.create(**{**data, "title": "Работа"})
    assert user.addresses.count() == 2
    with pytest.raises(IntegrityError), transaction.atomic():
        CustomerAddress.objects.create(**data, is_default=True)
    with pytest.raises(IntegrityError), transaction.atomic():
        CustomerProfile.objects.create(user=user)


def test_phone_and_coordinates_validation(user):
    user.phone = "invalid"
    with pytest.raises(ValidationError):
        user.full_clean()
    address = CustomerAddress(user=user, latitude=91, longitude=181)
    with pytest.raises(ValidationError) as error:
        address.full_clean()
    assert "latitude" in error.value.message_dict
    assert "longitude" in error.value.message_dict
