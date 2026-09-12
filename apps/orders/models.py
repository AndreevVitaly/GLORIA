import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import money_field
from apps.core.models import CreatedModel, TimestampedModel


class OrderStatus(models.Model):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_final = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return self.name


class Order(TimestampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_number = models.CharField(max_length=24, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, related_name="orders")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="operated_orders")
    recipient_name = models.CharField(max_length=160)
    recipient_phone = models.CharField(max_length=32)
    customer_phone = models.CharField(max_length=32)
    customer_email = models.EmailField()
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time_from = models.TimeField(null=True, blank=True)
    delivery_time_to = models.TimeField(null=True, blank=True)
    delivery_comment = models.TextField(blank=True)
    card_text = models.TextField(blank=True)
    subtotal = money_field(); discount_amount = money_field(); delivery_price = money_field(); total_amount = money_field()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self): return self.order_number


class OrderItem(CreatedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    custom_bouquet = models.ForeignKey("bouquet_builder.CustomBouquet", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=64, blank=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = money_field(); total_price = money_field()
    snapshot_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"


class OrderStatusHistory(CreatedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "История статуса"
        verbose_name_plural = "История статусов"
