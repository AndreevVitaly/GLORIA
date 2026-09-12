from django.contrib import admin
from .models import Order, OrderItem, OrderStatus, OrderStatusHistory

class ItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["total_price", "snapshot_data", "created_at"]

class HistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ["created_at"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "status", "recipient_name", "delivery_date", "total_amount", "created_at"]
    list_filter = ["status", "delivery_date"]
    search_fields = ["order_number", "recipient_name", "customer_phone", "customer_email"]
    inlines = [ItemInline, HistoryInline]

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "sort_order", "is_final"]
