import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from playwright.sync_api import expect

from kara.accounts.factories import UserFactory
from kara.accounts.views import AccountDeleteView


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

    def test_profile_template_render(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kara | Profile")
        self.assertContains(response, "Selected image: profile_default_image.png")

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

    def test_open_delete_account_modal(self, auth_page, live_server):
        # Tests interaction with the account deletion modal on the profile page.
        auth_page.goto(live_server.url + reverse("profile"))
        auth_page.get_by_role("button", name="Delete Account").click()
        modal_title = auth_page.locator("h3.modal-title")
        modal_content = auth_page.locator("div.modal-body")
        expect(modal_title).to_have_text("Do you really want to delete your account?")
        form_help_text = modal_content.locator("p#delete-account-form-help-text")
        expect(form_help_text).to_have_text(
            "※ To delete your account, please agree to all of the above statements."
        )
        form = auth_page.locator(f'form[action="{reverse("delete_account")}"]')
        assert form is not None

    def test_delete_account_modal_state_remember(self, auth_page, live_server):
        auth_page.goto(live_server.url + reverse("profile"))
        # To test the invalid case in the `DeleteAccountForm`,
        # remove the 'required' attribute from the `BooleanField`.
        for field_name, _ in AccountDeleteView.form_class.base_fields.items():
            auth_page.eval_on_selector(
                f'input[name="{field_name}"]', 'el => el.removeAttribute("required")'
            )
        auth_page.get_by_role("button", name="Delete Account").click()
        auth_page.locator("button#delete-account-button").click()
        # Check if the state of the delete modal is open.
        delete_modal_state = auth_page.get_attribute("div#delete_account", "x-data")
        assert "open: true" in delete_modal_state
        # Check whether the form contains error messages to verify
        # that the form inside the modal is preserved.
        confirm_irrecoverable_field = auth_page.locator(
            (
                "div#delete_account div.modal-body "
                "div.confirm_irrecoverable-field-container"
            )
        )
        error_cnt = confirm_irrecoverable_field.locator("ul li").count()
        assert error_cnt > 0
