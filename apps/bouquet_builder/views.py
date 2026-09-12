from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.catalog.models import FlowerVariant, GreeneryType, PackagingType

from .services.composer import CompositionError, create_saved_bouquet


def builder_context():
    return {
        "flower_variants": FlowerVariant.objects.filter(is_active=True).select_related(
            "flower_type", "flower_variety", "flower_color"
        ),
        "greenery_types": GreeneryType.objects.filter(is_active=True),
        "packaging_types": PackagingType.objects.filter(is_active=True),
    }


@require_http_methods(["GET"])
def builder(request):
    return render(request, "bouquet_builder/builder.html", builder_context())


@login_required
@require_http_methods(["POST"])
def save_bouquet(request):
    try:
        bouquet = create_saved_bouquet(user=request.user, data=request.POST)
    except CompositionError as error:
        messages.error(request, str(error))
        return render(request, "bouquet_builder/builder.html", builder_context(), status=400)
    messages.success(request, f"Букет «{bouquet.name}» сохранён в вашем кабинете.")
    return redirect("accounts:bouquets")
