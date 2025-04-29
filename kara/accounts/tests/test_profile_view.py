import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
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
        cls.profile = cls.user.profile
        cls.image = SimpleUploadedFile(
            name="cheeze_cake.jpg", content=b"cheeze cake", content_type="image/jpeg"
        )
        cls.url = reverse("profile")

    def setUp(self):
        self.client.force_login(self.user)

    def test_populate_initial_values(self):
        self.profile.bio = "bio initial value"
        self.profile.email_confirmed = True
        self.profile.bio_image = self.image
        self.profile.save()
        response = self.client.get(self.url)
        self.assertContains(response, 'src="/test_media/cheeze_cake.jpg"')
        self.assertContains(response, 'value="cheeze123"')
        self.assertContains(response, 'value="cheeze123@cake.com"')
        self.assertContains(response, "bio initial value")

    def test_email_confirm_field_help_text_template_render(self):
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "You have not verified your email yet. "
            "Some features may be limited until you verify your email.",
        )
        self.profile.email_confirmed = True
        self.profile.save()
        response = self.client.get(self.url)
        self.assertContains(response, "You have verified your email.")

    def test_update_profile_fields(self):
        new_bio = "Hello my name is cheeze-cake!!"
        response = self.client.post(
            self.url, {"username": self.user.username, "bio": new_bio}, follow=True
        )
        self.assertContains(response, new_bio)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, new_bio)

    def test_update_email_field(self):
        self.profile.email_confirmed = True
        self.profile.save()
        self.client.post(
            self.url,
            {"username": self.user.username, "email": "cheeze456@cake.com"},
            follow=True,
        )
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.email_confirmed)


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
