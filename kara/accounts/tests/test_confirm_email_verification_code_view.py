from django.test import Client, TestCase
from django.urls import reverse

from kara.accounts.models import User


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
        self.assertContains(response, "I'll confirm later!")

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

    def test_email_verification_fail(self):
        response = self.client.post(
            self.url,
            data={"code": 123456},
            follow=True,
        )
        self.assertContains(
            response, "<li>The verification code does not match.</li>", html=True
        )
