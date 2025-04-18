import pytest
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from playwright.sync_api import expect

from kara.accounts.factories import UserFactory


class ProfileViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="cheeze123", email="cheeze123@cake.com", password="password"
        )
        cls.url = reverse("profile")

    def setUp(self):
        self.client.force_login(self.user)

    def test_email_confirm_field_help_text_template_render(self):
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "You have not verified your email yet. "
            "Some features may be limited until you verify your email.",
        )
        self.user.profile.email_confirmed = True
        self.user.profile.save()
        response = self.client.get(self.url)
        self.assertContains(response, "You have verified your email.")


@pytest.mark.playwright
class TestPlaywright:

    def test_click_email_confirmation_button(self, auth_page, live_server):
        auth_page.goto(live_server.url + reverse("profile"))
        auth_page.get_by_role("button", name="Confirm Now!").click()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Kara Email Confirmation"
        assert "Hello tester, Welcome to Kara!" in mail.outbox[0].body
        expect(auth_page).to_have_title("Email Confirmation | Kara")
        expect(auth_page).to_have_url(live_server.url + reverse("email_confirmation"))
