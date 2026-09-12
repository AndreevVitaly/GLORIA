from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import GioiaUserChangeForm, GioiaUserCreationForm
from .models import (
    CustomerAddress,
    CustomerConnection,
    CustomerProfile,
    CustomerRecipient,
    RecipientCelebrationDate,
    Role,
    User,
    UserRole,
)


class SuperuserOnlyMixin:
    """Identity and permission administration must never enable staff self-escalation."""

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    has_add_permission = has_view_permission
    has_change_permission = has_view_permission
    has_delete_permission = has_view_permission


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    autocomplete_fields = ["role"]


@admin.register(User)
class GioiaUserAdmin(SuperuserOnlyMixin, UserAdmin):
    form = GioiaUserChangeForm
    add_form = GioiaUserCreationForm
    list_display = ["email", "first_name", "last_name", "phone", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering = ["email"]
    readonly_fields = ["uuid", "created_at", "updated_at", "date_joined", "last_login"]
    fieldsets = UserAdmin.fieldsets + (
        ("GIOIA", {"fields": ("uuid", "phone", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "phone", "password1", "password2"),
            },
        ),
    )
    inlines = [UserRoleInline]


@admin.register(Role)
class RoleAdmin(SuperuserOnlyMixin, admin.ModelAdmin):
    list_display = ["code", "name"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at"]
    filter_horizontal = ["permissions"]


@admin.register(UserRole)
class UserRoleAdmin(SuperuserOnlyMixin, admin.ModelAdmin):
    list_display = ["user", "role", "created_at"]
    list_filter = ["role"]
    autocomplete_fields = ["user", "role"]
    readonly_fields = ["created_at"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "birth_date", "marketing_consent"]
    search_fields = ["user__email"]
    readonly_fields = ["created_at", "updated_at"]
    exclude = ["avatar"]


@admin.register(CustomerConnection)
class CustomerConnectionAdmin(admin.ModelAdmin):
    list_display = ["user", "label", "created_at"]
    search_fields = ["user__email", "label"]
    readonly_fields = ["created_at", "updated_at"]


class CelebrationDateInline(admin.TabularInline):
    model = RecipientCelebrationDate
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


@admin.register(CustomerRecipient)
class CustomerRecipientAdmin(admin.ModelAdmin):
    list_display = ["name", "relationship", "phone", "user", "created_at"]
    search_fields = ["name", "relationship", "phone", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [CelebrationDateInline]


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "city", "recipient_name", "is_default"]
    list_filter = ["city", "is_default"]
    search_fields = ["user__email", "recipient_name", "street"]
    readonly_fields = ["created_at", "updated_at"]
