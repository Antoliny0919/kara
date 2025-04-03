from django.core import mail
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
        self.assertContains(response, "Please check your inbox!")
        self.assertTrue(User.objects.filter(username="strawberry").exists())
        self.assertFalse(
            User.objects.get(username="strawberry").profile.email_confirmed
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Kara Email Confirmation")
        self.assertIn(
            "Please enter the 6-digit email verification code on the "
            "email verification page.",
            mail.outbox[0].body,
        )
        self.assertIn("pending_email_confirmation", self.client.session)
        pending_email_confirmation = self.client.session["pending_email_confirmation"]
        self.assertEqual(pending_email_confirmation["username"], "strawberry")
        self.assertEqual(pending_email_confirmation["email"], "strawberry@farm.com")


class ConfirmEmailVerificationCodeViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.post(
            reverse("signup"),
            data={
                "username": "watermelon",
                "email": "watermelon@farm.com",
                "password1": "*password*",
                "password2": "*password*",
            },
        )
        self.url = reverse("email_confirmation")
        self.verification_code = self.client.session["pending_email_confirmation"][
            "code"
        ]

    def test_email_verification_template_render(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please check your inbox!")
        self.assertContains(response, "watermelon@farm.com")

    def test_email_verification_success(self):
        response = self.client.post(
            self.url,
            data={"code": self.verification_code},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="watermelon")
        self.assertTrue(user.profile.email_confirmed)
        self.assertNotIn("pending_email_confirmation", self.client.session)
