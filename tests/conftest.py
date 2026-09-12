import pytest

from apps.accounts.models import User
from apps.catalog.models import FlowerColor, FlowerType, FlowerVariant, FlowerVariety, GreeneryType


@pytest.fixture
def user(db):
    return User.objects.create_user(email="customer@example.com", password="Long-test-password-42")


@pytest.fixture
def variant(db):
    flower_type = FlowerType.objects.create(name="Роза", slug="rose")
    variety = FlowerVariety.objects.create(flower_type=flower_type, name="Red Naomi")
    color = FlowerColor.objects.create(name="Красный", slug="red", hex_color="#CC1122")
    return FlowerVariant.objects.create(
        flower_type=flower_type,
        flower_variety=variety,
        flower_color=color,
        sku="ROSE-RN-RED-60",
        stem_length_cm=60,
        purchase_price="90.50",
        retail_price="250.25",
    )


@pytest.fixture
def greenery(db):
    return GreeneryType.objects.create(name="Эвкалипт", slug="eucalyptus", retail_price="100.10")
