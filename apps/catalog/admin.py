from django.contrib import admin

from .models import (
    FlowerColor,
    FlowerType,
    FlowerVariant,
    FlowerVariety,
    GreeneryType,
    PackagingType,
)


class NamedCatalogAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    search_fields = ["name", "slug"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]


admin.site.register(FlowerType, NamedCatalogAdmin)
admin.site.register(GreeneryType, NamedCatalogAdmin)
admin.site.register(PackagingType, NamedCatalogAdmin)


@admin.register(FlowerVariety)
class FlowerVarietyAdmin(admin.ModelAdmin):
    list_display = ["name", "flower_type", "is_active"]
    list_filter = ["flower_type", "is_active"]
    search_fields = ["name"]
    autocomplete_fields = ["flower_type"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(FlowerColor)
class FlowerColorAdmin(admin.ModelAdmin):
    list_display = ["name", "hex_color", "is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at"]


@admin.register(FlowerVariant)
class FlowerVariantAdmin(admin.ModelAdmin):
    list_display = [
        "sku",
        "flower_type",
        "flower_variety",
        "flower_color",
        "stem_length_cm",
        "retail_price",
        "is_active",
    ]
    list_filter = ["flower_type", "flower_color", "is_active"]
    search_fields = ["sku", "flower_type__name", "flower_variety__name"]
    autocomplete_fields = ["flower_type", "flower_variety", "flower_color"]
    readonly_fields = ["created_at", "updated_at"]
