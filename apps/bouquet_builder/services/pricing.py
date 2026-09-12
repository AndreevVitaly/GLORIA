from decimal import Decimal

from django.db import transaction

from apps.bouquet_builder.models import CustomBouquet


@transaction.atomic
def refresh_component_totals(bouquet):
    """Stage-one admin totals from stored server-side component prices."""
    locked = CustomBouquet.objects.select_for_update().get(pk=bouquet.pk)
    subtotal = sum(
        (
            item.unit_price * item.quantity
            for items in [locked.flowers.all(), locked.greenery.all()]
            for item in items
        ),
        Decimal("0.00"),
    )
    locked.subtotal = subtotal
    locked.total_price = subtotal + locked.packaging_price + locked.addons_price
    locked.save(update_fields=["subtotal", "total_price", "updated_at"])
    bouquet.refresh_from_db()
    return bouquet
