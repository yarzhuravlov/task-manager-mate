import logging
import os
from typing import Any

from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View, generic
from django.views.decorators.csrf import csrf_exempt
from google.auth.transport import requests
from google.oauth2 import id_token

from accounts.forms import RegistrationForm, UsernameChangeForm
from accounts.services.emails.registration import send_account_activation_email
from accounts.tokens import account_activation_token
from base.utils.core import getattr_or_default
from workers.models import Position

User = get_user_model()

logger = logging.getLogger(__name__)


class RegistrationView(generic.CreateView):
    form_class = RegistrationForm
    template_name = "registration/register.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if form := getattr_or_default(self, "form"):
            context["form"] = form

        return context

    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        form = RegistrationForm(request.POST)

        if not form.is_valid():
            self.form = form
            return self.get(request, *args, **kwargs)

        with transaction.atomic():
            user = form.save(commit=False)
            user.is_active = False
            user.position = Position.get_unknown_position()
            user.save()

            current_site = get_current_site(request)
            domain = current_site.domain

            send_account_activation_email(
                user=user,
                domain=domain,
                uid=urlsafe_base64_encode(force_bytes(user.pk)),
                token=account_activation_token.make_token(user),
            )

        return render(request, "registration/ask_confirm.html")


class ActivateAccountView(View):
    def get(self, request: HttpRequest, pk: str, token: str):
        try:
            user = User.objects.get(pk=int(urlsafe_base64_decode(pk)))
        except (User.DoesNotExist, ValueError):
            user = None

        if user is not None and account_activation_token.check_token(
            user, token
        ):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(reverse("tasks:task-list"))
        else:
            logger.error(
                "Check of account activation token failed. "
                f"Url: {request.get_full_path()}"
            )
            return render(request, "registration/invalid_activation_link.html")


@method_decorator(csrf_exempt, name="dispatch")
class GoogleAuthReceiverView(View):
    def post(self, request, *args, **kwargs):
        token = request.POST["credential"]

        try:
            user_data = id_token.verify_oauth2_token(
                token, requests.Request(), os.environ["GOOGLE_OAUTH_CLIENT_ID"]
            )

            email = user_data["email"]
            first_name, last_name = user_data.get(
                "name", "Unknown Unknown"
            ).split()
            if given_name := user_data["given_name"]:
                first_name = given_name

            if family_name := user_data["family_name"]:
                last_name = family_name
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=email,
                    position=Position.get_unknown_position(),
                )

            login(request, user)
        except ValueError:
            return HttpResponse(status=403)

        return redirect(reverse("tasks:task-list"))


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["username_form"] = getattr_or_default(
            self,
            "username_form",
            UsernameChangeForm(instance=self.request.user),
        )

        return context

    def post(self, *args, **kwargs):
        if "username_form" in self.request.POST:
            username_form = UsernameChangeForm(
                self.request.POST, instance=self.request.user
            )
            if username_form.is_valid():
                username_form.save()
            else:
                self.username_form = username_form

        return super().get(*args, **kwargs)
