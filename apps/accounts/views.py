from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.bouquet_builder.models import CustomBouquet

from .forms import (
    AccountForm,
    CelebrationDateFormSet,
    ConnectionForm,
    CustomerLoginForm,
    ProfileForm,
    RecipientForm,
    SignupForm,
)
from .models import CustomerProfile
from .services import register_customer, save_customer_profile


class CustomerLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomerLoginForm
    redirect_authenticated_user = True


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = register_customer(form)
        except IntegrityError:
            form.add_error("email", "Не удалось создать аккаунт. Проверьте email.")
        else:
            login(request, user, backend="apps.accounts.backends.RoleBackend")
            messages.success(request, "Добро пожаловать в GIOIA! Ваш кабинет готов.")
            return redirect("accounts:profile")
    return render(request, "accounts/signup.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    customer, _ = CustomerProfile.objects.get_or_create(user=request.user)
    account_form = AccountForm(
        request.POST if request.method == "POST" else None, instance=request.user
    )
    profile_form = ProfileForm(
        request.POST if request.method == "POST" else None, request.FILES or None, instance=customer
    )
    if request.method == "POST":
        account_valid = account_form.is_valid()
        profile_valid = profile_form.is_valid()
        if account_valid and profile_valid:
            try:
                save_customer_profile(account_form, profile_form)
            except IntegrityError:
                account_form.add_error("email", "Не удалось сохранить данные. Проверьте email.")
            else:
                messages.success(request, "Ваши данные сохранены.")
                return redirect("accounts:profile")
    return render(
        request,
        "accounts/profile.html",
        {
            "account_form": account_form,
            "profile_form": profile_form,
            "customer": customer,
            "active_tab": "profile",
        },
    )


@login_required
def avatar(request):
    customer = get_object_or_404(CustomerProfile, user=request.user)
    if not customer.avatar:
        raise Http404
    try:
        response = FileResponse(customer.avatar.open("rb"), content_type="image/jpeg")
    except FileNotFoundError as error:
        raise Http404 from error
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def environment_context(request, form=None):
    page = Paginator(request.user.environment.all(), 20).get_page(request.GET.get("page"))
    return {
        "connections": page,
        "connection_form": form or ConnectionForm(),
        "active_tab": "environment",
    }


@login_required
@require_http_methods(["GET", "POST"])
def environment(request):
    form = ConnectionForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        connection = form.save(commit=False)
        connection.user = request.user
        connection.save()
        messages.success(request, "Запись добавлена в окружение.")
        return redirect("accounts:environment")
    return render(request, "accounts/environment.html", environment_context(request, form))


@login_required
@require_http_methods(["GET", "POST"])
def connection_edit(request, pk):
    connection = get_object_or_404(request.user.environment, pk=pk)
    form = ConnectionForm(request.POST if request.method == "POST" else None, instance=connection)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Запись обновлена.")
        return redirect("accounts:environment")
    return render(
        request,
        "accounts/connection_edit.html",
        {
            "form": form,
            "connection": connection,
            "active_tab": "environment",
        },
    )


@login_required
@require_POST
def connection_delete(request, pk):
    connection = get_object_or_404(request.user.environment, pk=pk)
    connection.delete()
    messages.success(request, "Запись удалена из окружения.")
    return redirect("accounts:environment")


@login_required
def recipients(request):
    queryset = request.user.recipients.prefetch_related("celebration_dates")
    page = Paginator(queryset, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "accounts/recipients.html",
        {"recipients": page, "active_tab": "recipients"},
    )


@login_required
def bouquets(request):
    saved_bouquets = (
        request.user.custom_bouquets.filter(status=CustomBouquet.Status.SAVED)
        .select_related("packaging")
        .prefetch_related("flowers__flower_variant__flower_type", "greenery__greenery_type")
    )
    return render(
        request,
        "accounts/bouquets.html",
        {"bouquets": saved_bouquets, "active_tab": "bouquets"},
    )


def recipient_forms(request, recipient=None):
    data = request.POST if request.method == "POST" else None
    form = RecipientForm(data, instance=recipient)
    formset = CelebrationDateFormSet(data, instance=recipient, prefix="dates")
    return form, formset


@login_required
@require_http_methods(["GET", "POST"])
def recipient_create(request):
    form, formset = recipient_forms(request)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            recipient = form.save(commit=False)
            recipient.user = request.user
            recipient.save()
            formset.instance = recipient
            formset.save()
        messages.success(request, "Адресат добавлен.")
        return redirect("accounts:recipients")
    return render(
        request,
        "accounts/recipient_form.html",
        {"form": form, "date_formset": formset, "active_tab": "recipients"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def recipient_edit(request, pk):
    recipient = get_object_or_404(request.user.recipients, pk=pk)
    form, formset = recipient_forms(request, recipient)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            form.save()
            formset.save()
        messages.success(request, "Данные адресата обновлены.")
        return redirect("accounts:recipients")
    return render(
        request,
        "accounts/recipient_form.html",
        {
            "form": form,
            "date_formset": formset,
            "recipient": recipient,
            "active_tab": "recipients",
        },
    )


@login_required
@require_POST
def recipient_delete(request, pk):
    recipient = get_object_or_404(request.user.recipients, pk=pk)
    recipient.delete()
    messages.success(request, "Адресат удалён.")
    return redirect("accounts:recipients")
