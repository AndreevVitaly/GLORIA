from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.content.views import home

admin.site.site_header = "GIOIA — управление магазином"
admin.site.site_title = "GIOIA"
admin.site.index_title = "Администрирование интернет-магазина"


def health(request):
    return JsonResponse({"project": "GIOIA", "stage": 1, "status": "ok"})


urlpatterns = [
    path("", home, name="home"),
    path("account/", include("apps.accounts.urls")),
    path("bouquets/", include("apps.bouquet_builder.urls")),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
]
