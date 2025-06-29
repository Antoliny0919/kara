from datetime import date

from django.test import TestCase, override_settings
from django.urls import reverse

from kara.wedding_gifts.factories import (
    CashGiftFactory,
    GiftTagFactory,
    InKindGiftFactory,
    UserFactory,
    WeddingGiftRegistryFactory,
)


@override_settings(DATE_FORMAT="F j, Y")
class GiftTableTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory(
            username="choco", email="choco@taste.com", password="password"
        )
        tag1 = GiftTagFactory.create(owner=cls.user, name="Family", hex_color="#527525")
        tag2 = GiftTagFactory.create(owner=cls.user, name="Friend", hex_color="#9965BA")
        registry = WeddingGiftRegistryFactory(owner=cls.user)
        cls.cash_gift = CashGiftFactory(
            registry=registry, price=100000000, receipt_date=date(2029, 12, 15)
        )
        cls.in_kind_gift = InKindGiftFactory(
            registry=registry,
            price=10000,
            receipt_date=date(2030, 7, 7),
            kind="appliance",
            kind_detail="very very loooo ooooo ooooo ooooo ooooo ooooo detail.",
        )
        cls.cash_gift.tags.set([tag1, tag2])
        cls.cash_gift.save()
        cls.in_kind_gift.tags.set([tag1, tag2])
        cls.in_kind_gift.save()
        cls.url = reverse("detail_registry", args=(registry.pk,))

    def setUp(self):
        self.client.force_login(self.user)

    def test_table_render_field_value(self):
        cash_gift_response = self.client.get(f"{self.url}?gift_type=cash")
        in_kind_gift_response = self.client.get(f"{self.url}?gift_type=in_kind")
        self.assertContains(in_kind_gift_response, "<td>Appliance</td>")
        self.assertContains(cash_gift_response, "<td>100,000,000</td>")
        self.assertContains(
            in_kind_gift_response,
            "<td>very very loooo ooooo ooooo ooooo ooooo ooooo …</td>",
        )
        self.assertContains(cash_gift_response, "<td>Dec. 15, 2029</td>")
        self.assertContains(
            cash_gift_response,
            (
                '<td><ul class="tags">\n'
                '<li style="background-color: #527525; color: white;">Family</li>\n'
                '<li style="background-color: #9965BA; color: white;">Friend</li>\n'
                "</ul></td>"
            ),
        )
