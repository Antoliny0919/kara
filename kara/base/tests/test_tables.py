from django.test import RequestFactory, TestCase

from kara.base.tables import Table

from .models import Fruit


class FruitTable(Table):
    pass


class TableTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Fruit.objects.create(name="hello", price=10000, expiration_date="2024-12-31")
        cls.factory = RequestFactory()
        cls.model = Fruit
        cls.queryset = Fruit.objects.all()

    def test_table_columns(self):
        request = self.factory.get("/fake-url/")
        table = FruitTable(request, self.model, self.queryset)
        self.assertEqual(table.columns, ["id", "name", "price", "expiration_date"])
        self.assertEqual(
            table.verbose_columns,
            ["Who are you!!", "Price expensive!!", "expiration date"],
        )
