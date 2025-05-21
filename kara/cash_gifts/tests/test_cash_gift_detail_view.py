import re

import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect

from kara.accounts.factories import UserFactory
from kara.cash_gifts.factories import CashGiftFactory, CashGiftRecordRepositoryFactory


class CashGiftRecordRepositoryDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="mango777", email="mango777@fruit.com", password="password"
        )
        repository = CashGiftRecordRepositoryFactory(owner=cls.user)
        cls.url = reverse("repository", args=(repository.pk,))
        cls.query_url = f"{cls.url}?page=1"

    def setUp(self):
        self.client.force_login(self.user)

    def test_template_response(self):
        response = self.client.get(self.url)
        self.assertNotIn("#cash-gifts-table", response.template_name[0])
        # Use partial template when it's an HTMX request with query string
        response = self.client.get(
            self.query_url,
            HTTP_HX_REQUEST="true",
        )
        self.assertIn("#cash-gifts-table", response.template_name[0])

    def test_form_context(self):
        response = self.client.get(self.url)
        self.assertIn("cash_gifts_form", response.context)
        response = self.client.get(self.query_url, HTTP_HX_REQUEST="true")
        self.assertNotIn("cash_gifts_form", response.context)


@pytest.mark.playwright
class TestPlaywright:

    @pytest.fixture
    def settings(self):
        with override_settings(CASH_GIFT_TABLE_LIST_PER_PAGE=10):
            yield

    @pytest.fixture
    def setup_data(self, settings, user):
        repository = CashGiftRecordRepositoryFactory(owner=user)
        for i in range(1, 201):
            CashGiftFactory.create(repository_id=repository.id, name=f"cash-gift-{i}")
        self.repository_pk = repository.pk

    def test_pagination(self, auth_page, live_server, setup_data):
        url = reverse("repository", args=(self.repository_pk,))
        auth_page.goto(live_server.url + f"{url}?page=5")
        current_page_button = auth_page.locator("nav.pagination em.current-page")
        expect(current_page_button).to_have_text("5")
        rows = auth_page.locator("div#cash-gifts-table table tbody tr")
        # Verify the table contents displayed on page 5
        expect(rows.first.locator("td").first).to_have_text("cash-gift-160")
        expect(rows.last.locator("td").first).to_have_text("cash-gift-151")
        auth_page.locator('nav.pagination a[href*="?page=8"]').click()
        expect(auth_page).to_have_url(re.compile(r"page=8"))
        rows = auth_page.locator("div#cash-gifts-table table tbody tr")
        # Verify the table contents displayed on page 8
        expect(rows.first.locator("td").first).to_have_text("cash-gift-130")
        expect(rows.last.locator("td").first).to_have_text("cash-gift-121")
        # Verify navigation by clicking the "Previous"
        # and "Next" buttons to change pages
        auth_page.locator("nav.pagination a.previous-page").click()
        expect(auth_page).to_have_url(re.compile(r"page=7"))
        auth_page.locator("nav.pagination a.next-page").click()
        expect(auth_page).to_have_url(re.compile(r"page=8"))
        auth_page.goto(live_server.url + url)
        previous_button = auth_page.locator("nav.pagination span", has_text="Previous")
        # Disable the "Previous" button when on the first page.
        expect(previous_button).to_contain_class("disabled")
        auth_page.goto(live_server.url + f"{url}?page=20")
        # Disable the "Next" button when on the last page.
        next_button = auth_page.locator("nav.pagination span", has_text="Next")
        expect(next_button).to_contain_class("disabled")
