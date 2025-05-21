from django.test import TestCase
from django.urls import reverse

from kara.accounts.factories import UserFactory
from kara.cash_gifts.factories import CashGiftFactory, CashGiftRecordRepositoryFactory


class CashGiftAddViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            username="black000", email="black000@color.com", password="password"
        )
        repository = CashGiftRecordRepositoryFactory(owner=cls.user)
        CashGiftFactory.create_batch(repository=repository, size=20)
        cls.url = reverse("add_cash_gift", args=(repository.pk,))

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
        self.assertContains(response, "<td>May 19, 2020</td>")
        self.assertIn("#cash-gifts-section", response.template_name[0])

    def test_reuse_before_selected_price_button(self):
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<input type="radio" name="price_0" value="1" required '
            'label="Price" id="id_price_0_0" checked>',
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
            'label="Price" id="id_price_0_1" checked>',
        )
