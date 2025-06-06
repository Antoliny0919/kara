import re

import pytest
from django.template.defaultfilters import urlencode
from django.test import TestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect

from kara.accounts.factories import UserFactory
from kara.wedding_gifts.factories import (
    CashGiftFactory,
    InKindGiftFactory,
    WeddingGiftRegistryFactory,
)


class CashGiftAddViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="black000", email="black000@color.com", password="password"
        )
        registry = WeddingGiftRegistryFactory(owner=cls.user)
        CashGiftFactory.create_batch(registry=registry, size=20)
        cls.url = reverse("cash_gift", args=(registry.pk,))

    def setUp(self):
        self.client.force_login(self.user)

    def test_add_cash_gift_object(self):
        response = self.client.post(
            self.url,
            data={
                "name": "Tim Bread",
                "price_0": "10000",
                "price_1": 10,
                "receipt_date_0": "2020",
                "receipt_date_1": "5",
                "receipt_date_2": "19",
            },
            HTTP_HX_REQUEST="true",
            follow=True,
        )
        self.assertContains(response, "<td>Tim Bread</td>")
        self.assertContains(response, "<td>100,000</td>")
        self.assertContains(response, "<td>2020-05-19</td>")
        self.assertIn("#gift-records-section", response.template_name[0])

    def test_reuse_before_selected_price_button(self):
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<input type="radio" name="price_0" value="1" required '
            'label="price" id="id_price_0_0" checked>',
        )

        response = self.client.post(
            self.url,
            {
                "name": "Tim Bread",
                "price_0": "10000",
                "price_1": 1,
                "receipt_date_0": "2024",
                "receipt_date_1": "7",
                "receipt_date_2": "21",
            },
        )
        # The previously selected button remains selected.
        self.assertContains(
            response,
            '<input type="radio" name="price_0" value="10000" required '
            'label="price" id="id_price_0_1" checked>',
        )


class WeddingGiftRegistryDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="mango777", email="mango777@fruit.com", password="password"
        )
        registry = WeddingGiftRegistryFactory(owner=cls.user)
        cls.registry_pk = registry.pk
        cls.url = reverse("detail_registry", args=(cls.registry_pk,))
        cls.query_url = f"{cls.url}?page=1"

    def setUp(self):
        self.client.force_login(self.user)

    def test_template_response(self):
        response = self.client.get(self.url)
        self.assertNotIn("#gift-records-table-section", response.template_name[0])
        # Use partial template when it's an HTMX request with query string
        response = self.client.get(
            self.query_url,
            HTTP_HX_REQUEST="true",
        )
        self.assertIn("#gift-records-table-section", response.template_name[0])

    def test_form_context(self):
        response = self.client.get(self.url)
        self.assertIn("gift_form", response.context)
        response = self.client.get(self.query_url, HTTP_HX_REQUEST="true")
        self.assertNotIn("gift_form", response.context)

    def test_context_from_mixin(self):
        response = self.client.get(self.url)
        self.assertIn("gift_type", response.context)
        self.assertEqual(response.context["gift_type"], "cash")
        self.assertEqual(
            response.context["gift_url"], reverse("cash_gift", args=(self.registry_pk,))
        )
        response = self.client.get(f"{self.url}?gift_type=in_kind")
        self.assertIn("gift_type", response.context)
        self.assertEqual(response.context["gift_type"], "in_kind")
        self.assertEqual(
            response.context["gift_url"],
            reverse("in_kind_gift", args=(self.registry_pk,)),
        )


@pytest.mark.playwright
class TestPlaywright:

    @pytest.fixture
    def settings(self):
        with override_settings(WEDDING_GIFT_REGISTRY_TABLE_LIST_PER_PAGE=10):
            yield

    @pytest.fixture
    def setup_data(self, settings, user):
        registry = WeddingGiftRegistryFactory(owner=user)
        for i in range(1, 201):
            CashGiftFactory.create(registry_id=registry.id, name=f"cash-gift-{i}")
        self.registry_pk = registry.pk

    def get_table_rows(self, auth_page):
        return auth_page.locator("section#gift-records-table-section table tbody tr")

    def test_pagination(self, auth_page, live_server, setup_data):
        url = reverse("detail_registry", args=(self.registry_pk,))
        auth_page.goto(live_server.url + f"{url}?page=5")
        current_page_button = auth_page.locator("nav.pagination em.current-page")
        expect(current_page_button).to_have_text("5")
        rows = auth_page.locator("section#gift-records-table-section table tbody tr")
        # Verify the table contents displayed on page 5
        expect(rows.first.locator("td").first).to_have_text("cash-gift-160")
        expect(rows.last.locator("td").first).to_have_text("cash-gift-151")
        auth_page.locator('nav.pagination a[href*="?page=8"]').click()
        expect(auth_page).to_have_url(re.compile(r"page=8"))
        rows = auth_page.locator("section#gift-records-table-section table tbody tr")
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

    def test_search(self, auth_page, live_server, user):
        usernames = ["Mookie Betts", "Ohtani Shohei", "Frederick Charles Freeman"]
        registry = WeddingGiftRegistryFactory(owner=user)
        for username in usernames:
            CashGiftFactory.create(registry_id=registry.id, name=username)

        url = reverse("detail_registry", args=(registry.pk,))
        auth_page.goto(live_server.url + url)
        search_input = auth_page.get_by_role("search").locator("input")
        search_input.fill("mookie betts")
        submit_button = auth_page.get_by_role("search").locator("button")
        submit_button.click()
        expect_url = f"search={urlencode("mookie betts")}"
        expect(auth_page).to_have_url(re.compile(rf"{expect_url}"))
        rows = auth_page.locator("section#gift-records-table-section table tbody tr")
        assert rows.count() == 1
        expect(rows.first.locator("td").first).to_have_text("Mookie Betts")
        search_input.fill("Ohtani Shohei")
        submit_button.click()
        expect_url = f"search={urlencode("Ohtani Shohei")}"
        expect(auth_page).to_have_url(re.compile(rf"{expect_url}"))
        rows = auth_page.locator("section#gift-records-table-section table tbody tr")
        assert rows.count() == 1
        expect(rows.first.locator("td").first).to_have_text("Ohtani Shohei")

    def test_change_gift_tab(self, auth_page, live_server, user):
        registry = WeddingGiftRegistryFactory(owner=user)
        CashGiftFactory.create(registry_id=registry.id, name="Kim Rich")
        InKindGiftFactory.create(registry_id=registry.id, name="Jang Poor")
        url = reverse("detail_registry", args=(registry.pk,))
        auth_page.goto(live_server.url + url)
        # Click 'In Kind Gift' tab
        # Verify that the InKindGift form and table are rendered correctly
        form_in_kind_select = auth_page.locator(
            "nav.tab-selector.gift-form ul li a:has-text('In Kind Gift')"
        )
        form_in_kind_select.click()
        expect(form_in_kind_select).to_contain_class("active")
        table_in_kind_select = auth_page.locator(
            "nav.tab-selector.gift-table ul li a:has-text('In Kind Gift')"
        )
        expect(table_in_kind_select).to_contain_class("active")
        form = auth_page.locator("form#gift-form")
        form_hx_post = form.get_attribute("hx-post")
        assert "in_kind_gift" in form_hx_post
        rows = auth_page.locator("section#gift-records-table-section table tbody tr")
        expect(rows.first.locator("td").first).to_have_text("Jang Poor")
        # Click 'Cash Gift' tab
        # Verify that the CashGift form and table are rendered correctly
        table_cash_select = auth_page.locator(
            "nav.tab-selector.gift-table ul li a:has-text('Cash Gift')"
        )
        table_cash_select.click()
        expect(table_cash_select).to_contain_class("active")
        form_cash_select = auth_page.locator(
            "nav.tab-selector.gift-form ul li a:has-text('Cash Gift')"
        )
        expect(form_cash_select).to_contain_class("active")
        form_hx_post = form.get_attribute("hx-post")
        assert "cash_gift" in form_hx_post
        expect(rows.first.locator("td").first).to_have_text("Kim Rich")

    def test_table_columns_ordering(self, auth_page, live_server, user):
        registry = WeddingGiftRegistryFactory(owner=user)
        cases = [
            {"name": "Alex", "price": 10000, "receipt_date": "2010-10-14"},
            {"name": "Sam", "price": 10000, "receipt_date": "2010-10-15"},
            {"name": "Jordan", "price": 10001, "receipt_date": "2010-10-13"},
            {"name": "Casey", "price": 9999, "receipt_date": "2010-10-14"},
            {"name": "Taylor", "price": 10002, "receipt_date": "2010-10-13"},
            {"name": "Morgan", "price": 10000, "receipt_date": "2010-10-16"},
            {"name": "Burdy", "price": 10001, "receipt_date": "2010-10-14"},
            {"name": "Loopy", "price": 9998, "receipt_date": "2010-10-17"},
        ]
        for case in cases:
            CashGiftFactory(registry_id=registry.id, **case)
        url = reverse("detail_registry", args=(registry.pk,))
        auth_page.goto(live_server.url + url)
        # order price ascending
        price_sort_button = auth_page.locator(
            "table thead tr th.sortable.column-price div a"
        )
        price_sort_button.click()
        expect(auth_page).to_have_url(re.compile(r"order=price"))
        rows = self.get_table_rows(auth_page)
        for i, text in enumerate(["Loopy", "Casey"]):
            expect(rows.nth(i).locator("td").first).to_have_text(text)
        # order price ascending & receipt_date(priority) ascending
        receipt_date_sort_button = auth_page.locator(
            "table thead tr th.sortable.column-receipt_date div a"
        )
        receipt_date_sort_button.click()
        expect(auth_page).to_have_url(re.compile(r"order=price&order=receipt_date"))
        rows = self.get_table_rows(auth_page)
        for i, text in enumerate(["Jordan", "Taylor", "Casey", "Alex", "Burdy"]):
            expect(rows.nth(i).locator("td").first).to_have_text(text)
        # order price descending & receipt_date(priority) ascending
        price_desc_button = auth_page.locator(
            "table thead tr th.sorted.column-price div.sortoptions a.toggle.descending"
        )
        price_desc_button.click()
        expect(auth_page).to_have_url(re.compile(r"order=-price&order=receipt_date"))
        for i, text in enumerate(["Taylor", "Jordan", "Burdy", "Alex", "Casey"]):
            expect(rows.nth(i).locator("td").first).to_have_text(text)
        # order receipt_date descending
        receipt_date_desc_button = auth_page.locator(
            "table thead tr th.sorted.column-receipt_date div.sortoptions "
            "a.toggle.descending"
        )
        receipt_date_desc_button.click()
        price_remove_sort_button = auth_page.locator(
            "table thead tr th.sorted.column-price div.sortoptions a.sortremove"
        )
        price_remove_sort_button.click()
        expect(auth_page).to_have_url(re.compile(r"order=-receipt_date"))
        for i, text in enumerate(["Loopy", "Morgan", "Sam"]):
            expect(rows.nth(i).locator("td").first).to_have_text(text)
