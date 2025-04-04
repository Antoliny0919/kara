from django.core import mail
from django.test import TestCase
from django.urls import reverse

from kara.accounts.factories import UserFactory


class ResendEmailConfirmationViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(username="mango", email="mango@farm.com")
        cls.url = reverse("email_confirmation_resend")

    def setUp(self):
        self.client.force_login(self.user)

    def test_redirect_template_render(self):
        response = self.client.post(self.url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please check your inbox!")
        self.assertContains(response, "mango@farm.com")

    def test_resend_email(self):
        self.client.post(self.url, {}, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Kara Email Confirmation")
        self.assertIn(
            "Please enter the 6-digit email verification code on the "
            "email verification page.",
            mail.outbox[0].body,
        )
