from django.urls import path

from . import views

app_name = "bouquet_builder"

urlpatterns = [
    path("create/", views.builder, name="builder"),
    path("create/save/", views.save_bouquet, name="save"),
]
