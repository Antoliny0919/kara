from django.core import mail
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
        self.button_class = (
            "text-kara-strong hover:text-kara-deep transition-colors duration-500"
        )

    def test_email_verification_template_render(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please check your inbox!")
        self.assertContains(response, "watermelon@farm.com")
        # Check later confirm button
        login_link = reverse("login")
        self.assertContains(
            response,
            '<a href="%s" class="%s">I\'ll confirm later!</a>'
            % (login_link, self.button_class),
        )

    def test_email_verification_success(self):
        response = self.client.post(
            self.url,
            data={"code": self.verification_code, "action_confirm": "1"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="watermelon")
        self.assertTrue(user.profile.email_confirmed)
        self.assertNotIn("pending_email_confirmation", self.client.session)

    def test_email_verification_fail(self):
        response = self.client.post(
            self.url,
            data={"code": 123456, "action_confirm": "1"},
            follow=True,
        )
        self.assertContains(
            response, "<li>The verification code does not match.</li>", html=True
        )

    def test_resend_email_confirmation_code(self):
        mail_cnt = len(mail.outbox)
        response = self.client.post(
            self.url,
            data={"action_resend": "1"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), mail_cnt + 1)
        self.assertEqual(mail.outbox[-1].subject, "Kara Email Confirmation")
        self.assertIn(
            "Please enter the 6-digit email verification code on the "
            "email verification page.",
            mail.outbox[-1].body,
        )
