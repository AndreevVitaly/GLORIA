from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class RoleBackend(ModelBackend):
    """Standard Django permissions plus explicit role grants; no implicit role bypass."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is not None:
            username = username.strip().lower()
        if "email" in kwargs:
            kwargs["email"] = kwargs["email"].strip().lower()
        return super().authenticate(request, username=username, password=password, **kwargs)

    def get_group_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        permissions = super().get_group_permissions(user_obj, obj)
        role_permissions = Permission.objects.filter(gioia_roles__users=user_obj).values_list(
            "content_type__app_label", "codename"
        )
        return permissions | {f"{app}.{code}" for app, code in role_permissions}
