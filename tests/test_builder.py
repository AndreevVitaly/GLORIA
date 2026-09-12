from decimal import Decimal

import pytest
from django.urls import reverse

from apps.bouquet_builder.models import CustomBouquet
from apps.catalog.models import PackagingType

pytestmark = pytest.mark.django_db


def test_builder_shows_active_catalog_components(client, variant, greenery):
    response = client.get(reverse("bouquet_builder:builder"))

    assert response.status_code == 200
    assert variant.sku in response.content.decode()
    assert greenery.name in response.content.decode()


def test_guest_cannot_save_bouquet(client, variant):
    response = client.post(reverse("bouquet_builder:save"), {f"flower-{variant.pk}": "3"})

    assert response.status_code == 302
    assert reverse("accounts:login") in response.url
    assert not CustomBouquet.objects.exists()


def test_customer_saves_composed_bouquet_with_server_prices(client, user, variant, greenery):
    packaging = PackagingType.objects.create(name="Лента", slug="ribbon", price="99.50")
    client.force_login(user)

    response = client.post(
        reverse("bouquet_builder:save"),
        {
            "name": "Для мамы",
            f"flower-{variant.pk}": "3",
            f"greenery-{greenery.pk}": "2",
            "packaging": str(packaging.pk),
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:bouquets")
    bouquet = CustomBouquet.objects.get()
    assert bouquet.user == user
    assert bouquet.name == "Для мамы"
    assert bouquet.packaging == packaging
    assert bouquet.total_price == Decimal("1050.45")
    assert bouquet.flowers.get().unit_price == Decimal("250.25")
    assert bouquet.greenery.get().unit_price == Decimal("100.10")


def test_builder_rejects_tampered_or_empty_composition(client, user, variant):
    client.force_login(user)
    response = client.post(reverse("bouquet_builder:save"), {f"flower-{variant.pk}": "100"})

    assert response.status_code == 400
    assert not CustomBouquet.objects.exists()
