from decimal import Decimal

import pytest
from django.contrib.admin.models import LogEntry

from apps.accounts.models import User
from apps.bouquet_builder.models import CustomBouquet

pytestmark = pytest.mark.django_db


def test_admin_add_bouquet_uses_catalog_prices(client, variant, greenery):
    admin = User.objects.create_superuser(
        email="florist@example.com", password="Strong-password-94"
    )
    client.force_login(admin)
    response = client.post(
        "/admin/bouquet_builder/custombouquet/add/",
        {
            "name": "Тестовый букет",
            "status": "draft",
            "composition_seed": "18452",
            "subtotal": "0.01",
            "total_price": "0.01",
            "flowers-TOTAL_FORMS": "1",
            "flowers-INITIAL_FORMS": "0",
            "flowers-MIN_NUM_FORMS": "0",
            "flowers-MAX_NUM_FORMS": "1000",
            "flowers-0-flower_variant": str(variant.pk),
            "flowers-0-quantity": "7",
            "flowers-0-unit_price": "0.01",
            "greenery-TOTAL_FORMS": "1",
            "greenery-INITIAL_FORMS": "0",
            "greenery-MIN_NUM_FORMS": "0",
            "greenery-MAX_NUM_FORMS": "1000",
            "greenery-0-greenery_type": str(greenery.pk),
            "greenery-0-quantity": "2",
            "greenery-0-unit_price": "0.01",
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    bouquet = CustomBouquet.objects.get()
    assert bouquet.total_price == Decimal("1951.95")
    assert bouquet.flowers.get().unit_price == Decimal("250.25")
    assert bouquet.greenery.get().unit_price == Decimal("100.10")
    assert LogEntry.objects.filter(user=admin, object_id=str(bouquet.pk)).exists()
