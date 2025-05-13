from datetime import date

from django.forms import TextInput
from django.forms.widgets import (
    CheckboxInput,
    EmailInput,
    MultiWidget,
    PasswordInput,
    RadioSelect,
    Textarea,
    TextInput,
)


class KaraRadioSelect(RadioSelect):
    template_name = "base/widgets/radio.html"


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
            return [value.day, value.month, value.year]
        elif isinstance(value, str):
            year, month, day = value.split("-")
            return [year, month, day]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        year, month, day = super().value_from_datadict(data, files, name)
        # DateField expects a single string that it can parse into a date.
        return "{}-{}-{}".format(year, month, day)
