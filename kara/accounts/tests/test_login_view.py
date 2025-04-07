from django.test import TestCase
from django.urls import reverse

from kara.accounts.factories import UserFactory


class LoginViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="egg123", email="egg123@cookie.com", password="password"
        )
        cls.user.set_password(cls.user.password)
        cls.user.save()
        cls.url = reverse("login")

    def test_login(self):
        response = self.client.post(
            self.url,
            {
                "username": "egg123",
                "password": "password",
            },
        )
        self.assertEqual(response.url, "/")
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            self.url,
            {
                "username": "egg123@cookie.com",
                "password": "password",
            },
        )
        self.assertEqual(response.url, "/")
        self.assertEqual(response.status_code, 302)
