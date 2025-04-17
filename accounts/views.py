import logging
from typing import Any

from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View, generic

from accounts.forms import RegistrationForm
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
                token=account_activation_token.make_token(user)
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
