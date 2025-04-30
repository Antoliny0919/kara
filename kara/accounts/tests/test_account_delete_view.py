from django.test import TestCase
from django.urls import reverse

from kara.accounts.factories import UserFactory
from kara.accounts.models import User


class AccountDeleteViewTests(TestCase):

    def setUp(self):
        self.user = UserFactory(
            username="tuna123", email="tuna123@ocean.com", password="password"
        )
        self.url = reverse("delete_account")
        self.client.force_login(self.user)

    def test_delete_account_success(self):
        response = self.client.post(
            self.url,
            {
                "confirm_irrecoverable": True,
                "confirm_data_loss": True,
            },
        )
        self.assertEqual(response.url, "/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="tuna123").exists())
