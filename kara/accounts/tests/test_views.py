from django.test import Client, TestCase
from django.urls import reverse

from kara.accounts.models import User


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signup")

    def test_signup_template_render(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registration")

    def test_signup_success(self):
        response = self.client.post(
            self.url,
            data={
                "username": "strawberry",
                "email": "strawberry@farm.com",
                "password1": "*password*",
                "password2": "*password*",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="strawberry").exists())
