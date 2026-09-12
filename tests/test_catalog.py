import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from apps.catalog.models import FlowerColor, FlowerType, FlowerVariant, FlowerVariety, PackagingType

pytestmark = pytest.mark.django_db


def test_variant_relations_and_optional_variety(variant):
    variant.full_clean()
    assert variant.flower_variety.flower_type == variant.flower_type
    variant.flower_variety = None
    variant.stem_length_cm = None
    variant.full_clean()
    variant.save()
    assert FlowerVariant.objects.get(pk=variant.pk).flower_variety is None


def test_wrong_variety_rejected_on_save(variant):
    tulip = FlowerType.objects.create(name="Тюльпан", slug="tulip")
    variant.flower_variety = FlowerVariety.objects.create(flower_type=tulip, name="Strong Gold")
    with pytest.raises(ValidationError):
        variant.save()


@pytest.mark.parametrize(
    "field,value",
    [
        ("purchase_price", "-0.01"),
        ("retail_price", "-1.00"),
        ("stem_length_cm", 0),
    ],
)
def test_variant_database_constraints(variant, field, value):
    with pytest.raises(IntegrityError), transaction.atomic():
        FlowerVariant.objects.filter(pk=variant.pk).update(**{field: value})


def test_unique_sku(variant):
    variant.pk = None
    with pytest.raises(IntegrityError), transaction.atomic():
        variant.save()


def test_color_validation():
    color = FlowerColor(name="Красный", slug="red", hex_color="red")
    with pytest.raises(ValidationError):
        color.full_clean()


def test_catalog_protected_deletion(variant):
    with pytest.raises(ProtectedError):
        variant.flower_type.delete()
    with pytest.raises(ProtectedError):
        variant.flower_color.delete()


def test_packaging_and_scale_constraints():
    with pytest.raises(IntegrityError), transaction.atomic():
        PackagingType.objects.create(name="Крафт", slug="kraft", price="-1")
    with pytest.raises(IntegrityError), transaction.atomic():
        FlowerType.objects.create(name="Пион", slug="peony", default_scale=0)
