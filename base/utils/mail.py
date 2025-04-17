import logging
from typing import Any
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from base.utils.core import execute_in_background

logger = logging.getLogger(__name__)


@execute_in_background
def send_email(
    subject: str,
    html_template: str,
    context: dict[str, Any],
    to_email=None,
):
    subject: str = subject
    to_email: str | list[str] = to_email
    cc: list[str] | None = context.get("cc")
    bcc: list[str] | None = context.get("bcc")
    attachments = context.get("attachments")

    if not to_email:
        raise ValueError(
            "The 'to_email' address must be provided and cannot be empty."
        )
    elif not isinstance(to_email, list):
        to_email = [to_email]

    try:
        html_message = render_to_string(html_template, context)
        message = EmailMessage(
            subject=subject,
            body=html_message,
            to=to_email,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
        )
        message.content_subtype = "html"
        result = message.send()
        logger.info(
            f"Sending email to {', '.join(to_email)} "
            f"with subject: {subject} - Status {result}"
        )
    except Exception as e:
        logger.info(
            f"Sending email to {', '.join(to_email)} "
            "with subject: {subject} - Status 0"
        )
        logger.exception(e)
