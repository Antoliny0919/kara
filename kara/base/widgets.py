from datetime import date

from django.forms import TextInput
from django.forms.widgets import (
    CheckboxInput,
    EmailInput,
    MultiWidget,
    NumberInput,
    PasswordInput,
    RadioSelect,
    Textarea,
    TextInput,
)


class KaraRadioSelect(RadioSelect):
    template_name = "base/widgets/radio_select.html"


class KaraEmailInput(EmailInput):
    template_name = "base/widgets/input.html"


class KaraPasswordInput(PasswordInput):
    template_name = "base/widgets/input.html"


class KaraTextarea(Textarea):
    template_name = "base/widgets/textarea.html"


class KaraTextInput(TextInput):
    template_name = "base/widgets/input.html"


class KaraCheckboxInput(CheckboxInput):
    template_name = "base/widgets/checkbox.html"


class KaraSplitDateInput(MultiWidget):
    template_name = "base/widgets/date.html"

    def __init__(self, attrs=None):
        widgets = [
            TextInput(attrs={"placeholder": "YYYY", "maxlength": "4", **(attrs or {})}),
            TextInput(attrs={"placeholder": "MM", "maxlength": "2", **(attrs or {})}),
            TextInput(attrs={"placeholder": "DD", "maxlength": "2", **(attrs or {})}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, date):
            return [value.year, value.month, value.day]
        elif isinstance(value, str):
            year, month, day = value.split("-")
            return [year, month, day]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        year, month, day = super().value_from_datadict(data, files, name)
        # DateField expects a single string that it can parse into a date.
        return "{}-{}-{}".format(year, month, day)


class UnitNumberInput(MultiWidget):
    template_name = "base/widgets/unit_number_input.html"

    def __init__(self, attrs=None, choices=()):
        widgets = [
            RadioSelect(attrs=(attrs or {}), choices=choices),
            NumberInput(attrs=(attrs or {})),
        ]
        super().__init__(widgets, attrs=None)
        self.choices = choices

    def decompress(self, value):
        if value and isinstance(value, dict):
            # Initial data must be provided as a dictionary.
            # e.g. {"select": "10", "number": 1000}
            return [value.get("select"), value.get("number")]
        return [None, None]
