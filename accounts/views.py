from typing import Any
from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View, generic

from accounts.forms import RegistrationForm
from accounts.tokens import account_activation_token
from base.utils import getattr_or_default
from workers.models import Position

User = get_user_model()


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

        user = form.save(commit=False)
        user.is_active = False
        user.position = Position.get_unknown_position()
        user.save()

        current_site = get_current_site(request)
        mail_subject = "Activate your Task Manager account."
        message = render_to_string(
            "emails/acc_active_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": user.pk,
                "token": account_activation_token.make_token(user),
            },
        )
        to_email = form.cleaned_data["email"]
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return render(request, "registration/ask_confirm.html")


class ActivateAccountView(View):
    def get(self, request: HttpRequest, pk: int, token: str):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            user = None

        if user is not None and account_activation_token.check_token(
            user, token
        ):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(reverse("tasks:task-list"))
        else:
            return render(request, "registration/invalid_activation_link.html")
