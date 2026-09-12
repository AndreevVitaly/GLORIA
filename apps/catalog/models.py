from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.core.models import CreatedModel, TimestampedModel


def money_field():
    return models.DecimalField(
        "Цена",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )


class NamedCatalogModel(TimestampedModel):
    name = models.CharField("Название", max_length=150)
    slug = models.SlugField("Адрес (slug)", max_length=150, unique=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        abstract = True
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name


class FlowerType(NamedCatalogModel):
    default_layer = models.IntegerField("Слой по умолчанию", default=10)
    default_scale = models.DecimalField(
        "Масштаб по умолчанию",
        max_digits=6,
        decimal_places=3,
        default=Decimal("1.000"),
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    class Meta(NamedCatalogModel.Meta):
        db_table = "flower_types"
        verbose_name = "Вид цветка"
        verbose_name_plural = "Виды цветов"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(default_scale__gt=0), name="flower_type_scale_positive"
            )
        ]


class FlowerVariety(TimestampedModel):
    flower_type = models.ForeignKey(
        FlowerType, verbose_name="Вид цветка", on_delete=models.PROTECT, related_name="varieties"
    )
    name = models.CharField("Название", max_length=150)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        db_table = "flower_varieties"
        verbose_name = "Сорт цветка"
        verbose_name_plural = "Сорта цветов"
        ordering = ["name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["flower_type", "name"], name="flower_variety_type_name_unique"
            )
        ]

    def __str__(self):
        return f"{self.flower_type} / {self.name}"


class FlowerColor(CreatedModel):
    name = models.CharField("Название", max_length=100)
    hex_color = models.CharField(
        "Цвет HEX",
        max_length=7,
        validators=[RegexValidator(r"^#[0-9a-fA-F]{6}$", "Используйте HEX-цвет #RRGGBB.")],
    )
    slug = models.SlugField("Адрес (slug)", max_length=100, unique=True)
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        db_table = "flower_colors"
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name


class FlowerVariant(TimestampedModel):
    flower_type = models.ForeignKey(
        FlowerType, verbose_name="Вид цветка", on_delete=models.PROTECT, related_name="variants"
    )
    flower_variety = models.ForeignKey(
        FlowerVariety,
        verbose_name="Сорт",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="variants",
    )
    flower_color = models.ForeignKey(
        FlowerColor, verbose_name="Цвет", on_delete=models.PROTECT, related_name="variants"
    )
    sku = models.CharField("Артикул", max_length=64, unique=True)
    stem_length_cm = models.PositiveSmallIntegerField(
        "Длина стебля, см", null=True, blank=True, validators=[MinValueValidator(1)]
    )
    purchase_price = money_field()
    purchase_price.verbose_name = "Закупочная цена"
    retail_price = money_field()
    retail_price.verbose_name = "Розничная цена"
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        db_table = "flower_variants"
        verbose_name = "Вариант цветка"
        verbose_name_plural = "Варианты цветов"
        ordering = ["sku"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(purchase_price__gte=0), name="flower_purchase_price_nonnegative"
            ),
            models.CheckConstraint(
                condition=models.Q(retail_price__gte=0), name="flower_retail_price_nonnegative"
            ),
            models.CheckConstraint(
                condition=models.Q(stem_length_cm__isnull=True) | models.Q(stem_length_cm__gt=0),
                name="flower_stem_length_positive",
            ),
        ]

    def clean(self):
        super().clean()
        if self.flower_variety_id and self.flower_type_id:
            if self.flower_variety.flower_type_id != self.flower_type_id:
                raise ValidationError(
                    {"flower_variety": "Сорт должен относиться к выбранному виду."}
                )

    def save(self, *args, **kwargs):
        # Cross-table consistency cannot be expressed by a regular CHECK constraint.
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sku} · {self.flower_type} / {self.flower_color}"


class GreeneryType(NamedCatalogModel):
    retail_price = money_field()
    retail_price.verbose_name = "Розничная цена"

    class Meta(NamedCatalogModel.Meta):
        db_table = "greenery_types"
        verbose_name = "Вид зелени"
        verbose_name_plural = "Зелень"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(retail_price__gte=0), name="greenery_price_nonnegative"
            )
        ]


class PackagingType(NamedCatalogModel):
    price = money_field()

    class Meta(NamedCatalogModel.Meta):
        db_table = "packaging_types"
        verbose_name = "Вид упаковки"
        verbose_name_plural = "Виды упаковки"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="packaging_price_nonnegative"
            )
        ]
