from django import forms
from django.test import SimpleTestCase

from kara.base.fields import UnitNumberField


class FishForm(forms.Form):
    name = forms.CharField(max_length=128)
    price = UnitNumberField(choices=[("1", 1), ("100", 100), ("10000", 10000)])


class UnitNumberFieldTests(SimpleTestCase):

    def test_compress(self):
        case = [
            ({"name": "salmon", "price_0": "10000", "price_1": 20}, 200000),
            ({"name": "mackerel", "price_0": "1", "price_1": 4000}, 4000),
        ]
        for data, expected_price in case:
            with self.subTest(data=data):
                form = FishForm(data=data)
                form.is_valid()
                self.assertEqual(form.cleaned_data["price"], expected_price)
        form = FishForm(data=data)

    def test_decompress(self):
        form = FishForm(initial={"price": {"select": "100", "number": 10}})
        # Initial value is 100, so it's checked
        self.assertIn(
            '<input type="radio" name="price_0" value="100" required '
            'id="id_price_0_1" checked>',
            form.as_div(),
        )
        # Initial value is 10, so number input have value 10
        self.assertIn(
            '<input id="id_price_1" type="number" name="price_1" '
            'value="10" required id="id_price_1" placeholder=" ">',
            form.as_div(),
        )
