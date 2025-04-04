from django.urls import path

from accounts.views import ActivateAccountView, RegistrationView


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "activate/<str:pk>/<str:token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
]
