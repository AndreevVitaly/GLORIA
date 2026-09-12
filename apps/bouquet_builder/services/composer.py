from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from apps.catalog.models import FlowerVariant, GreeneryType, PackagingType

from ..models import CustomBouquet, CustomBouquetFlower, CustomBouquetGreenery
from .pricing import refresh_component_totals


class CompositionError(ValueError):
    """A submitted bouquet cannot be composed from the current catalog."""


@dataclass(frozen=True)
class Composition:
    flowers: dict[int, int]
    greenery: dict[int, int]
    packaging_id: int | None


def _quantity(value):
    try:
        quantity = int(value)
    except (TypeError, ValueError) as error:
        raise CompositionError("Количество должно быть целым числом.") from error
    if not 0 <= quantity <= 99:
        raise CompositionError("Количество каждого компонента — от 0 до 99.")
    return quantity


def parse_composition(data):
    flowers, greenery = {}, {}
    for key, value in data.items():
        for prefix, destination in (("flower-", flowers), ("greenery-", greenery)):
            if key.startswith(prefix):
                try:
                    component_id = int(key.removeprefix(prefix))
                except ValueError as error:
                    raise CompositionError("Некорректный компонент букета.") from error
                quantity = _quantity(value)
                if quantity:
                    destination[component_id] = quantity
    if not flowers:
        raise CompositionError("Добавьте в букет хотя бы один цветок.")
    packaging_raw = data.get("packaging", "")
    try:
        packaging_id = int(packaging_raw) if packaging_raw else None
    except ValueError as error:
        raise CompositionError("Некорректная упаковка.") from error
    return Composition(flowers=flowers, greenery=greenery, packaging_id=packaging_id)


@transaction.atomic
def create_saved_bouquet(*, user, data):
    composition = parse_composition(data)
    flowers = FlowerVariant.objects.filter(pk__in=composition.flowers, is_active=True)
    greenery = GreeneryType.objects.filter(pk__in=composition.greenery, is_active=True)
    if flowers.count() != len(composition.flowers) or greenery.count() != len(composition.greenery):
        raise CompositionError("Один из выбранных компонентов больше недоступен.")
    packaging = None
    if composition.packaging_id:
        packaging = PackagingType.objects.filter(
            pk=composition.packaging_id, is_active=True
        ).first()
        if packaging is None:
            raise CompositionError("Выбранная упаковка больше недоступна.")

    bouquet = CustomBouquet.objects.create(
        user=user,
        name=data.get("name", "").strip()[:200] or "Мой букет",
        status=CustomBouquet.Status.SAVED,
        packaging=packaging,
        packaging_price=packaging.price if packaging else Decimal("0.00"),
        total_price=packaging.price if packaging else Decimal("0.00"),
        preview_data={
            "flowers": composition.flowers,
            "greenery": composition.greenery,
            "packaging": packaging.name if packaging else "Без упаковки",
        },
    )
    for flower in flowers:
        CustomBouquetFlower.objects.create(
            custom_bouquet=bouquet,
            flower_variant=flower,
            quantity=composition.flowers[flower.pk],
            unit_price=flower.retail_price,
        )
    for item in greenery:
        CustomBouquetGreenery.objects.create(
            custom_bouquet=bouquet,
            greenery_type=item,
            quantity=composition.greenery[item.pk],
            unit_price=item.retail_price,
        )
    return refresh_component_totals(bouquet)
