import factory
import pytest
from django.test import TestCase
from django.urls import reverse
from playwright.sync_api import expect

from kara.accounts.factories import UserFactory
from kara.wedding_gifts.factories import (
    CashGiftFactory,
    InKindGiftFactory,
    WeddingGiftRegistryFactory,
)
from kara.wedding_gifts.models import WeddingGiftRegistry


class RegistryAddViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="samdasu123", email="samdasu123@water.com", password="password"
        )
        cls.registry = WeddingGiftRegistryFactory(owner=cls.user)

    def setUp(self):
        self.client.force_login(self.user)

    def test_add_new_registry(self):
        self.client.post(
            reverse("add_registry"),
            data={
                "cover_image": "test/image.png",
                "side": "Groom",
                "receiver": "evian",
                "receptionist": "isis",
                "wedding_date_0": "1999",
                "wedding_date_1": "7",
                "wedding_date_2": "29",
            },
            follow=True,
        )
        registry = WeddingGiftRegistry.objects.filter(receiver="evian")
        self.assertTrue(registry.exists())


class RegistryDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="samdasu123", email="samdasu123@water.com", password="password"
        )
        cls.registry = WeddingGiftRegistryFactory.create(
            owner=cls.user,
            side="Groom",
            receiver="Purple",
            receptionist="Orange",
        )
        cls.url = reverse("detail_registry", args=(cls.registry.pk,))
        cash_gift_prices = [10000, 50000, 100000, 200000, 500000]
        cls.total_cash_gift_price = sum(cash_gift_prices)
        CashGiftFactory.create_batch(
            5,
            price=factory.Iterator(cash_gift_prices),
            registry=cls.registry,
        )
        in_kind_gift_prices = [70000, 170000, 370000]
        cls.total_in_kind_gift_price = sum(in_kind_gift_prices)
        InKindGiftFactory.create_batch(
            3,
            price=factory.Iterator(in_kind_gift_prices),
            registry=cls.registry,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_template_render(self):
        response = self.client.get(self.url)
        # Simple registry insight value
        self.assertContains(response, f'data-count="{self.total_cash_gift_price}"')
        self.assertContains(response, 'data-count="5"')
        self.assertContains(response, f'data-count="{self.total_in_kind_gift_price}"')
        self.assertContains(response, 'data-count="3"')
        total_price = self.total_cash_gift_price + self.total_in_kind_gift_price
        self.assertContains(response, f'data-count="{total_price}"')

    def test_update_registry(self):
        response = self.client.post(
            self.url,
            data={
                "cover_image": self.registry.cover_image,
                "side": "Bride",
                "receiver": "Green",
                "receptionist": "Blue",
                "wedding_date_0": "2003",
                "wedding_date_1": "8",
                "wedding_date_2": "6",
            },
            follow=True,
        )
        self.registry.refresh_from_db()
        self.assertEqual(self.registry.side, "Bride")
        self.assertEqual(self.registry.receiver, "Green")
        self.assertEqual(self.registry.receptionist, "Blue")
        self.assertContains(
            response, "The wedding gift registry has been successfully updated!"
        )


@pytest.mark.playwright
class TestPlaywright:

    def test_preview_registry(self, auth_page, live_server):
        auth_page.goto(live_server.url + reverse("add_registry"))
        preview = auth_page.locator("div#wedding-gift-records-preview")
        cover_image = auth_page.locator("div#id_cover_image")
        cover_image.locator("button").click()

        # Check if the selected image has been applied to the preview.
        images = cover_image.locator("ul.image-select-list li")
        images.first.click()
        select_image = images.first.locator("img").get_attribute("src")
        selected_image = preview.locator("img").get_attribute("src")
        assert select_image == selected_image

        # Check if the selected side is displayed in the preview.
        display_side = preview.locator("span#display_side")
        bride_side = auth_page.locator('div#id_side input[value="Bride"]')
        expect(display_side).to_have_text("Groom's side")
        bride_side.click()
        expect(display_side).to_have_text("Bride's side")

        # Check if the filled receiver is displayed in the preview.
        display_receiver = preview.locator("span#display_receiver")
        expect(display_receiver).to_have_text("?")
        auth_page.locator("input#id_receiver").fill("Earth")
        expect(display_receiver).to_have_text("Earth")

        # Check if the filled receptionist is displayed in the preview.
        display_receptionist = preview.locator("span#display_receptionist")
        expect(display_receptionist).to_have_text("?")
        auth_page.locator("input#id_receptionist").fill("Mars")
        expect(display_receptionist).to_have_text("Mars")

        # Check if the filled wedding_date is displayed in the preview.
        display_wedding_date = [
            preview.locator(f"span#display_wedding_date_{i}") for i in range(3)
        ]
        for node in display_wedding_date:
            expect(node).to_have_text("?")
        wedding_date_value = ["1988", "7", "22"]
        for i, value in enumerate(wedding_date_value):
            auth_page.locator(f"input#id_wedding_date_{i}").fill(value)
            expect(preview.locator(f"span#display_wedding_date_{i}")).to_have_text(
                value
            )
