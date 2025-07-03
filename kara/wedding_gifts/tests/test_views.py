import re

import pytest
from django.db.models.query import QuerySet
from django.template.defaultfilters import urlencode
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views.generic import ListView
from playwright.sync_api import expect

from kara.accounts.factories import UserFactory
from kara.base.tests.models import Fish
from kara.wedding_gifts.factories import (
    CashGiftFactory,
    InKindGiftFactory,
    WeddingGiftRegistryFactory,
)
from kara.wedding_gifts.models import GiftTag
from kara.wedding_gifts.views import WeddingGiftRegistryContextMixin


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
            HTTP_HX_TARGET="gift-records-section",
            follow=True,
        )
        self.assertContains(response, "<td>Tim Bread</td>")
        self.assertContains(response, "<td>100,000</td>")
        self.assertContains(response, "<td>2020-05-19</td>")

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


class FishView(WeddingGiftRegistryContextMixin, ListView):
    template_name = "blue_fish.html"
    model = Fish


class TestWeddingGiftRegistryContextMixin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.view = FishView.as_view()
        cls.user = UserFactory(
            username="lazy777", email="lazy777@mong.com", password="password"
        )

    def test_dynamic_add_template_name(self):
        case = [
            ("some_htmx_target", "blue_fish.html", "wedding_gifts/base.html"),
            ("registry-selector", "wedding_gifts/base.html", "blue_fish.html"),
        ]
        for hx_target, expected_exist, expected_not_exist in case:
            request = self.factory.get("/fake-url/", HTTP_HX_TARGET=hx_target)
            request.htmx = True
            request.user = self.user
            response = self.view(request)
            self.assertIn(expected_exist, response.template_name)
            self.assertNotIn(expected_not_exist, response.template_name)

    def test_context_data(self):
        request = self.factory.get("/fake-url/")
        request.htmx = False
        request.user = self.user
        response = self.view(request)
        self.assertIn("registries", response.context_data)
        registries = response.context_data["registries"]
        self.assertTrue(isinstance(registries, QuerySet))


@pytest.mark.playwright
class TestPlaywright:

    @pytest.fixture
    def settings(self):
        with override_settings(WEDDING_GIFT_REGISTRY_TABLE_LIST_PER_PAGE=10):
            yield

    @pytest.fixture
    def setup_gifts(self, settings, user):
        registry = WeddingGiftRegistryFactory(owner=user)
        for i in range(1, 201):
            CashGiftFactory.create(registry_id=registry.id, name=f"cash-gift-{i}")
        self.registry_pk = registry.pk

    @pytest.fixture
    def setup_tags(self, user):
        registry = WeddingGiftRegistryFactory(owner=user)
        tags_data = [
            (
                {
                    "name": "Friend",
                    "description": "My best friend",
                    "hex_color": "#34588E",
                }
            ),
            (
                {
                    "name": "Family",
                    "description": (
                        "My family, including my relatives" "up to the fourth degree"
                    ),
                    "hex_color": "#527525",
                }
            ),
            (
                {
                    "name": "Escape King",
                    "description": "The best escape room club in Korea",
                    "hex_color": "#1AACAE",
                }
            ),
        ]
        for tag_data in tags_data:
            GiftTag.objects.create(owner=user, **tag_data)
        self.registry = registry
        self.tags_data = tags_data

    def get_table_rows(self, auth_page):
        return auth_page.locator("section#gift-records-table-section table tbody tr")

    def test_pagination(self, auth_page, live_server, setup_gifts):
        url = reverse("detail_registry", args=(self.registry_pk,))
        auth_page.goto(live_server.url + f"{url}?page=5")
        current_page_button = auth_page.locator("nav.pagination em.current-page")
        expect(current_page_button).to_have_text("5")
        rows = auth_page.locator("section#gift-records-table-section table tbody tr")
        # Verify the table contents displayed on page 5
        expect(rows.first.locator("td").first).to_have_text("cash-gift-160")
        expect(rows.last.locator("td").first).to_have_text("cash-gift-151")
        auth_page.locator('nav.pagination a[hx-get*="?page=8"]').click()
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

    def test_tag_select_widget_dropdown_panel_visible(
        self, auth_page, live_server, setup_tags
    ):
        auth_page.goto(live_server.url + self.registry.get_absolute_url())
        # The dropdown panel is in a hidden state.
        dropdown_panel = auth_page.locator("div#id_tags-dropdown-panel")
        assert dropdown_panel.is_visible() is False
        tag_select = auth_page.locator(
            "form#gift-form div.field-container div#id_tags-dropdown-trigger button"
        )
        tag_select.click()
        # The dropdown panel becomes visible when a specific button is clicked.
        dropdown_panel = auth_page.locator("div#id_tags-dropdown-panel")
        expect(dropdown_panel).to_be_visible()

    def test_tag_node_data(self, auth_page, live_server, setup_tags):
        auth_page.goto(live_server.url + self.registry.get_absolute_url())
        tag_select = auth_page.locator(
            "form#gift-form div.field-container div#id_tags-dropdown-trigger button"
        )
        tag_select.click()

        from_block = auth_page.locator("div#id_tags-dropdown-panel ul li#id_tags_from")
        tags = from_block.locator("ul li").all()
        assert len(tags) == 3

        gift_tags = list(GiftTag.objects.all())
        # Rendering test for elements inside the dropdown panel.
        for index, data in enumerate(zip(tags, self.tags_data)):
            tag, expected = data
            input = tag.locator("input[type=checkbox]")
            label = tag.locator("label")
            tag_symbol_color = label.locator("span.color")
            tag_info = label.locator("span.info div")
            expect(input).to_have_value(str(gift_tags[index].id))
            expect(tag_symbol_color).to_have_attribute(
                "style", f"background-color: {expected["hex_color"]}"
            )
            expect(tag_info.nth(0)).to_have_text(expected["name"])
            expect(tag_info.nth(1)).to_have_text(expected["description"])

    def test_tag_select_widget_move_tag(self, auth_page, live_server, setup_tags):
        auth_page.goto(live_server.url + self.registry.get_absolute_url())
        tag_select = auth_page.locator(
            "form#gift-form div.field-container div#id_tags-dropdown-trigger button"
        )
        tag_select.click()

        from_block = auth_page.locator("div#id_tags-dropdown-panel ul li#id_tags_from")
        from_block_tags = from_block.locator("ul li")
        to_block = auth_page.locator("div#id_tags-dropdown-panel ul li#id_tags_to")
        to_block_tags = to_block.locator("ul li")
        # Currently, no tags are selected.
        assert to_block_tags.count() == 0

        # from -> to
        from_first_tag = from_block_tags.first
        moved_element_html = from_first_tag.inner_html()
        from_first_tag.click()

        # Specific tag was selected via click from the 'from' list.
        assert to_block_tags.count() == 1

        to_first_tag = to_block_tags.first
        assert moved_element_html == str(to_first_tag.inner_html())

        # to -> from
        moved_element_html = to_first_tag.inner_html()
        to_first_tag.click()

        assert to_block_tags.count() == 0
        assert from_block_tags.count() == 3

        # Moved tag is added as the last element of the block.
        from_last_tag = from_block_tags.last
        assert moved_element_html == str(from_last_tag.inner_html())

    def test_selected_tags_display(self, auth_page, live_server, setup_tags):
        auth_page.goto(live_server.url + self.registry.get_absolute_url())
        tag_select = auth_page.locator(
            "form#gift-form div.field-container div#id_tags-dropdown-trigger button"
        )
        tag_select.click()

        from_block = auth_page.locator("div#id_tags-dropdown-panel ul li#id_tags_from")
        tags = from_block.locator("ul li")

        expected_label = []
        # Select the last two tags.
        for _ in range(2):
            tag = tags.last
            label = tag.locator("label")
            tag_info = label.locator("span.info div")
            expected_label.append(tag_info.nth(0).inner_text())
            tag.click()

        # Close dropdown panel
        tag_select.click()

        # Selected tags are present in the selected tags area.
        selected_tags = auth_page.locator(
            "form#gift-form div.field-container ul#id_tags-dropdown-result li"
        ).all()
        for tag in selected_tags:
            assert tag.inner_text() in expected_label
