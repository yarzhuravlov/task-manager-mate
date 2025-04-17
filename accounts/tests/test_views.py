from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.forms import RegistrationForm
from accounts.tokens import account_activation_token
from workers.models import Position

User = get_user_model()


class RegistrationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.factory = RequestFactory()

        self.unknown_position = Position.objects.create(name="Unknown")

        self.position_patcher = patch(
            "workers.models.Position.get_unknown_position"
        )
        self.mock_get_unknown_position = self.position_patcher.start()
        self.mock_get_unknown_position.return_value = self.unknown_position

        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        }

        self.site_patcher = patch("accounts.views.get_current_site")
        self.mock_get_current_site = self.site_patcher.start()

        self.mock_site = MagicMock()
        self.mock_site.domain = "testserver"
        self.mock_get_current_site.return_value = self.mock_site

    def tearDown(self):
        self.position_patcher.stop()
        self.site_patcher.stop()

    def test_get_registration_page(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")
        self.assertIsInstance(response.context["form"], RegistrationForm)

    @patch("accounts.views.send_account_activation_email")
    def test_successful_registration(self, mock_send_email):
        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/ask_confirm.html")

        user = User.objects.get(username=self.valid_data["username"])
        self.assertFalse(user.is_active)
        self.assertEqual(user.position, self.unknown_position)

        self.assertTrue(mock_send_email.called)
        call_args = mock_send_email.call_args[1]
        self.assertEqual(call_args["user"], user)
        self.assertEqual(call_args["domain"], "testserver")
        self.assertIn("uid", call_args)
        self.assertIn("token", call_args)

    def test_invalid_registration_form(self):
        invalid_data = self.valid_data.copy()
        invalid_data.pop("password2")

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "registration/register.html",
        )

        self.assertTrue(response.context["form"].errors)

        self.assertFalse(
            User.objects.filter(username=self.valid_data["username"]).exists()
        )

    @patch("accounts.views.transaction.atomic")
    @patch("accounts.views.send_account_activation_email")
    def test_transaction_atomic_used(self, mock_send_email, mock_atomic):
        """Test that transaction.atomic is used when registering a user."""
        mock_atomic.return_value.__enter__.return_value = None
        mock_atomic.return_value.__exit__.return_value = None

        self.client.post(self.register_url, self.valid_data)

        mock_atomic.assert_called_once()

    @patch("accounts.views.send_account_activation_email")
    def test_get_current_site_called(self, mock_send_email):
        self.client.post(self.register_url, self.valid_data)

        self.mock_get_current_site.assert_called_once()


class ActivateAccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="testpassword123",
            is_active=False,
            position=Position.get_unknown_position(),
        )

        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

        self.activation_url = reverse(
            "activate",
            kwargs={"pk": self.uid, "token": self.token},
        )

        self.logger_patcher = patch("accounts.views.logger")
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        self.logger_patcher.stop()

    def test_valid_activation(self):
        self.assertFalse(self.user.is_active)

        response = self.client.get(self.activation_url)

        self.assertRedirects(response, reverse("tasks:task-list"))

        self.user.refresh_from_db()

        self.assertTrue(self.user.is_active)

        self.assertEqual(
            int(self.client.session["_auth_user_id"]), self.user.pk
        )

    def test_invalid_user_id(self):
        invalid_uid = urlsafe_base64_encode(force_bytes(999999))
        invalid_url = reverse(
            "activate",
            kwargs={"pk": invalid_uid, "token": self.token},
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "registration/invalid_activation_link.html"
        )

        self.mock_logger.error.assert_called_once()

    def test_invalid_token(self):
        invalid_url = reverse(
            "activate",
            kwargs={"pk": self.uid, "token": "invalid-token"},
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "registration/invalid_activation_link.html"
        )

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        self.mock_logger.error.assert_called_once()

    @patch("accounts.tokens.account_activation_token.check_token")
    def test_token_verification_used(self, mock_check_token):
        mock_check_token.return_value = True

        self.client.get(self.activation_url)

        mock_check_token.assert_called_once_with(self.user, self.token)
