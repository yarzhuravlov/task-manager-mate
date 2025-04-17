from django.contrib.auth.models import AbstractUser

from base.services.emails.base import BaseEmailService


class AccountActivationEmailService(BaseEmailService):
    subject = "Activate your Task Manager account."
    template_name_html = "emails/acc_active_email.html"


def send_account_activation_email(
    user: AbstractUser,
    domain: str,
    uid: str,
    token: str,
):
    account_activation_email_service = AccountActivationEmailService(
        {
            "user": user,
            "domain": domain,
            "uid": uid,
            "token": token,
        },
        user.email,
    )
    account_activation_email_service.send()
