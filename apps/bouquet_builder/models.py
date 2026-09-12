import secrets
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import money_field
from apps.core.models import CreatedModel, TimestampedModel


def generate_seed():
    return secrets.randbits(63)


class CustomBouquet(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SAVED = "saved", "Сохранён"
        ARCHIVED = "archived", "Архив"

    uuid = models.UUIDField("UUID", default=uuid.uuid4, unique=True, editable=False)
    packaging = models.ForeignKey(
        "catalog.PackagingType",
        verbose_name="Упаковка",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="custom_bouquets",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="custom_bouquets",
    )
    name = models.CharField("Название", max_length=200, default="Мой букет")
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.DRAFT)
    composition_seed = models.PositiveBigIntegerField("Seed композиции", default=generate_seed)
    subtotal = money_field()
    subtotal.verbose_name = "Стоимость компонентов"
    packaging_price = money_field()
    packaging_price.verbose_name = "Стоимость упаковки"
    addons_price = money_field()
    addons_price.verbose_name = "Стоимость дополнений"
    total_price = money_field()
    total_price.verbose_name = "Итоговая стоимость"
    preview_svg = models.TextField("Предпросмотр SVG", blank=True)
    preview_data = models.JSONField("Данные предпросмотра", default=dict, blank=True)

    class Meta:
        db_table = "custom_bouquets"
        verbose_name = "Пользовательский букет"
        verbose_name_plural = "Пользовательские букеты"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=["draft", "saved", "archived"]),
                name="bouquet_valid_status",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    subtotal__gte=0, packaging_price__gte=0, addons_price__gte=0, total_price__gte=0
                ),
                name="bouquet_prices_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    total_price=models.F("subtotal")
                    + models.F("packaging_price")
                    + models.F("addons_price")
                ),
                name="bouquet_total_matches",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.uuid})"


class CustomBouquetFlower(CreatedModel):
    custom_bouquet = models.ForeignKey(
        CustomBouquet, verbose_name="Букет", on_delete=models.CASCADE, related_name="flowers"
    )
    flower_variant = models.ForeignKey(
        "catalog.FlowerVariant",
        verbose_name="Вариант цветка",
        on_delete=models.PROTECT,
        related_name="bouquet_items",
    )
    quantity = models.PositiveIntegerField("Количество", validators=[MinValueValidator(1)])
    unit_price = money_field()
    unit_price.verbose_name = "Цена за единицу"

    class Meta:
        db_table = "custom_bouquet_flowers"
        verbose_name = "Цветок в букете"
        verbose_name_plural = "Цветы в букете"
        constraints = [
            models.UniqueConstraint(
                fields=["custom_bouquet", "flower_variant"], name="bouquet_flower_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name="bouquet_flower_quantity_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0), name="bouquet_flower_price_nonnegative"
            ),
        ]

    def __str__(self):
        return f"{self.flower_variant} × {self.quantity}"


class CustomBouquetGreenery(CreatedModel):
    custom_bouquet = models.ForeignKey(
        CustomBouquet, verbose_name="Букет", on_delete=models.CASCADE, related_name="greenery"
    )
    greenery_type = models.ForeignKey(
        "catalog.GreeneryType",
        verbose_name="Вид зелени",
        on_delete=models.PROTECT,
        related_name="bouquet_items",
    )
    quantity = models.PositiveIntegerField("Количество", validators=[MinValueValidator(1)])
    unit_price = money_field()
    unit_price.verbose_name = "Цена за единицу"

    class Meta:
        db_table = "custom_bouquet_greenery"
        verbose_name = "Зелень в букете"
        verbose_name_plural = "Зелень в букете"
        constraints = [
            models.UniqueConstraint(
                fields=["custom_bouquet", "greenery_type"], name="bouquet_greenery_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name="bouquet_greenery_quantity_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0), name="bouquet_greenery_price_nonnegative"
            ),
        ]

    def __str__(self):
        return f"{self.greenery_type} × {self.quantity}"
