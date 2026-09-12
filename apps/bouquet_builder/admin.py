from django.contrib import admin

from .models import CustomBouquet, CustomBouquetFlower, CustomBouquetGreenery


class BouquetFlowerInline(admin.TabularInline):
    model = CustomBouquetFlower
    extra = 0
    autocomplete_fields = ["flower_variant"]
    readonly_fields = ["unit_price", "created_at"]


class BouquetGreeneryInline(admin.TabularInline):
    model = CustomBouquetGreenery
    extra = 0
    autocomplete_fields = ["greenery_type"]
    readonly_fields = ["unit_price", "created_at"]


@admin.register(CustomBouquet)
class CustomBouquetAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "packaging", "status", "total_price", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "user__email", "uuid"]
    readonly_fields = [
        "uuid",
        "subtotal",
        "packaging_price",
        "addons_price",
        "total_price",
        "preview_svg",
        "preview_data",
        "created_at",
        "updated_at",
    ]
    inlines = [BouquetFlowerInline, BouquetGreeneryInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for deleted in formset.deleted_objects:
            deleted.delete()
        for instance in instances:
            component = (
                instance.flower_variant
                if isinstance(instance, CustomBouquetFlower)
                else instance.greenery_type
            )
            instance.unit_price = component.retail_price
            instance.save()
        formset.save_m2m()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        from .services.pricing import refresh_component_totals

        refresh_component_totals(form.instance)
