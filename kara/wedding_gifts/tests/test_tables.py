from datetime import date

from django.test import RequestFactory, TestCase, override_settings

from kara.base.tests.models import Cake
from kara.wedding_gifts.tables import GiftTable


class CakeTable(GiftTable):
    pass


@override_settings(DATE_FORMAT="F j, Y")
class GiftTableTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cake = Cake.objects.create(
            name="Cheese Basque Cake",
            kind="cheese",
            kind_detail=(
                "Cheese basque cake with italian cheese made by korea's best baker."
            ),
            price=100000000,
            expiration_date=date(2029, 12, 31),
        )
        cls.factory = RequestFactory()
        cls.model = Cake
        cls.queryset = Cake.objects.all()

    def test_display_field_value(self):
        request = self.factory.get("/fake-url/")
        table = CakeTable(request, self.model, self.queryset)
        choice_value = table.display_for_value(self.cake, "kind")
        self.assertEqual(choice_value, "Cheese")
        price_value = table.display_for_value(self.cake, "price")
        self.assertEqual(price_value, "100,000,000")
        truncated_str_value = table.display_for_value(self.cake, "kind_detail")
        self.assertEqual(
            truncated_str_value, "Cheese basque cake with italian cheese made by …"
        )
        date_value = table.display_for_value(self.cake, "expiration_date")
        self.assertEqual(str(date_value), "Dec. 31, 2029")
