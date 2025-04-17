from typing import Callable, Any
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings


def dummy_execute_in_background(function: Callable[..., Any]):
    return function


patch(
    "base.utils.core.execute_in_background", dummy_execute_in_background
).start()

from base.utils.mail import send_email # noqa:  E401


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class SendEmailTests(TestCase):
    @patch("base.utils.mail.render_to_string")
    @patch("base.utils.mail.EmailMessage")
    def test_send_email_success(
        self, mock_email_message, mock_render_to_string
    ):
        mock_render_to_string.return_value = "<p>Test Email Content</p>"

        mock_email_instance = MagicMock()
        mock_email_instance.send.return_value = 1
        mock_email_message.return_value = mock_email_instance

        send_email(
            subject="Test Subject",
            html_template="test_template.html",
            context={"key": "value"},
            to_email="test@example.com",
        )

        mock_render_to_string.assert_called_once_with(
            "test_template.html", {"key": "value"}
        )
        mock_email_message.assert_called_once_with(
            subject="Test Subject",
            body="<p>Test Email Content</p>",
            to=["test@example.com"],
            cc=None,
            bcc=None,
            attachments=None,
        )
        mock_email_instance.send.assert_called_once()

    @patch("base.utils.mail.render_to_string")
    @patch("base.utils.mail.EmailMessage")
    def test_send_email_no_recipient(
        self,
        mock_email_message,
        mock_render_to_string,
    ):
        with self.assertRaises(ValueError) as context:
            send_email(
                subject="Test Subject",
                html_template="test_template.html",
                context={"key": "value"},
                to_email=None,
            )

        self.assertEqual(
            str(context.exception),
            "The 'to_email' address must be provided and cannot be empty.",
        )

        mock_render_to_string.assert_not_called()
        mock_email_message.assert_not_called()

    @patch("base.utils.mail.render_to_string")
    @patch("base.utils.mail.EmailMessage")
    def test_send_email_failure(
        self, mock_email_message, mock_render_to_string
    ):
        mock_render_to_string.return_value = "<p>Test Email Content</p>"

        mock_email_instance = MagicMock()
        mock_email_instance.send.side_effect = Exception(
            "Email sending failed"
        )
        mock_email_message.return_value = mock_email_instance

        with self.assertLogs("base.utils.mail", level="INFO") as log:
            send_email(
                subject="Test Subject",
                html_template="test_template.html",
                context={"key": "value"},
                to_email="test@example.com",
            )

        self.assertIn(
            "Sending email to test@example.com with subject: "
            "Test Subject - Status 0",
            log.output[-2],
        )
