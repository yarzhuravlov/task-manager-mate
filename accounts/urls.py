from django.urls import path

from accounts.views import (
    ActivateAccountView,
    RegistrationView,
    GoogleAuthReceiverView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "activate/<str:pk>/<str:token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path(
        "google-auth-receiver",
        GoogleAuthReceiverView.as_view(),
        name="google-auth-receiver",
    ),
]
