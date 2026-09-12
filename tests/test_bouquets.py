from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from apps.bouquet_builder.models import CustomBouquet, CustomBouquetFlower, CustomBouquetGreenery
from apps.bouquet_builder.services.pricing import refresh_component_totals

pytestmark = pytest.mark.django_db


def test_bouquet_composition_storage_and_totals(user, variant, greenery):
    preview = {"seed": 18452, "elements": [{"variant_id": variant.pk, "x": 42, "y": 21}]}
    bouquet = CustomBouquet.objects.create(
        user=user,
        composition_seed=18452,
        preview_data=preview,
        preview_svg='<svg xmlns="http://www.w3.org/2000/svg"/>',
    )
    CustomBouquetFlower.objects.create(
        custom_bouquet=bouquet, flower_variant=variant, quantity=7, unit_price=variant.retail_price
    )
    CustomBouquetGreenery.objects.create(
        custom_bouquet=bouquet, greenery_type=greenery, quantity=2, unit_price=greenery.retail_price
    )
    refresh_component_totals(bouquet)
    assert bouquet.total_price == Decimal("1951.95")
    assert bouquet.preview_data == preview
    assert bouquet.composition_seed == 18452
    assert bouquet.preview_svg.startswith("<svg")
    variant.retail_price = Decimal("999.99")
    variant.save()
    refresh_component_totals(bouquet)
    assert bouquet.total_price == Decimal("1951.95")


def test_guest_and_independent_json_defaults():
    first = CustomBouquet.objects.create()
    second = CustomBouquet.objects.create()
    first.preview_data["x"] = 1
    assert second.preview_data == {}
    assert first.user is None
    assert first.uuid != second.uuid
    assert 0 <= first.composition_seed < 2**63


@pytest.mark.parametrize("kind", ["flower", "greenery"])
@pytest.mark.parametrize("field,value", [("quantity", 0), ("unit_price", "-1")])
def test_component_database_constraints(variant, greenery, kind, field, value):
    bouquet = CustomBouquet.objects.create()
    model, component = (
        (CustomBouquetFlower, {"flower_variant": variant})
        if kind == "flower"
        else (CustomBouquetGreenery, {"greenery_type": greenery})
    )
    data = {"quantity": 1, "unit_price": "1.00", **component, field: value}
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.create(custom_bouquet=bouquet, **data)


def test_duplicates_protection_and_cascade(variant):
    bouquet = CustomBouquet.objects.create()
    data = dict(custom_bouquet=bouquet, flower_variant=variant, quantity=1, unit_price="250.25")
    CustomBouquetFlower.objects.create(**data)
    with pytest.raises(IntegrityError), transaction.atomic():
        CustomBouquetFlower.objects.create(**data)
    with pytest.raises(ProtectedError):
        variant.delete()
    bouquet.delete()
    assert not CustomBouquetFlower.objects.exists()
    assert variant.__class__.objects.filter(pk=variant.pk).exists()


@pytest.mark.parametrize(
    "values",
    [
        {"total_price": "1"},
        {"subtotal": "-1", "total_price": "-1"},
        {"status": "invalid"},
    ],
)
def test_bouquet_totals_and_status_constraints(values):
    with pytest.raises(IntegrityError), transaction.atomic():
        CustomBouquet.objects.create(**values)


def test_user_deletion_preserves_bouquet(user):
    bouquet = CustomBouquet.objects.create(user=user)
    user.delete()
    bouquet.refresh_from_db()
    assert bouquet.user is None
