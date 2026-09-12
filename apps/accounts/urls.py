from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.profile, name="profile"),
    path("login/", views.CustomerLoginView.as_view(), name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("avatar/", views.avatar, name="avatar"),
    path(
        "password/",
        PasswordChangeView.as_view(
            template_name="accounts/password.html", success_url=reverse_lazy("accounts:profile")
        ),
        name="password",
    ),
    path("environment/", views.environment, name="environment"),
    path("environment/<int:pk>/edit/", views.connection_edit, name="connection_edit"),
    path("environment/<int:pk>/delete/", views.connection_delete, name="connection_delete"),
    path("recipients/", views.recipients, name="recipients"),
    path("bouquets/", views.bouquets, name="bouquets"),
    path("recipients/add/", views.recipient_create, name="recipient_create"),
    path("recipients/<int:pk>/edit/", views.recipient_edit, name="recipient_edit"),
    path("recipients/<int:pk>/delete/", views.recipient_delete, name="recipient_delete"),
]
