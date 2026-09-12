from django.db import transaction

from .models import CustomerProfile, Role, UserRole


@transaction.atomic
def register_customer(form):
    user = form.save()
    role, _ = Role.objects.get_or_create(code=Role.Code.CUSTOMER, defaults={"name": "Покупатель"})
    UserRole.objects.create(user=user, role=role)
    CustomerProfile.objects.create(user=user)
    return user


@transaction.atomic
def save_customer_profile(account_form, profile_form):
    user = account_form.save(commit=False)
    user.save(update_fields=["phone", "first_name", "email", "updated_at"])
    profile = CustomerProfile.objects.select_for_update().get(pk=profile_form.instance.pk)
    profile.birth_date = profile_form.cleaned_data["birth_date"]
    profile.gender = profile_form.cleaned_data["gender"]
    old_name = profile.avatar.name
    photo = profile_form.cleaned_data.get("photo")
    remove = profile_form.cleaned_data.get("remove_photo")
    if photo:
        profile.avatar = photo
    elif remove:
        profile.avatar = ""
    profile.save()
    if old_name and (photo or remove):
        storage = profile.avatar.storage
        transaction.on_commit(lambda: storage.delete(old_name))
    return profile
