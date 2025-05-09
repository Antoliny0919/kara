from datetime import date

from django import forms
from django.test import SimpleTestCase

from kara.base.widgets import KaraSplitDateInput


class EventForm(forms.Form):
    place = forms.CharField(max_length=128)
    event_date = forms.DateField(widget=KaraSplitDateInput)


class KaraSplitDateInputWidgetTests(SimpleTestCase):

    def test_decompress(self):
        case = [
            (date(1970, 5, 5), 1970, 5, 5),
            ("1988-12-31", 1988, 12, 31),
        ]
        for value, year, month, day in case:
            with self.subTest(initial_value=value):
                form = EventForm(initial={"event_date": value})
                self.assertIn(f'value="{year}"', form.as_div())
                self.assertIn(f'value="{month}"', form.as_div())
                self.assertIn(f'value="{day}"', form.as_div())

    def test_value_from_datadict(self):
        data = {
            "place": "illinois",
            "event_date_0": "2010",
            "event_date_1": "05",
            "event_date_2": "10",
        }
        form = EventForm(data)
        form.is_valid()
        self.assertTrue(isinstance(form.cleaned_data["event_date"], date))
        self.assertEqual(str(form.cleaned_data["event_date"]), "2010-05-10")
