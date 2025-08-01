import os
from datetime import date

from django.conf import settings
from django.core.files.storage import default_storage
from django.forms import CheckboxSelectMultiple, NumberInput, TextInput
from django.forms.widgets import (
    CheckboxInput,
    ChoiceWidget,
    EmailInput,
    MultiWidget,
    NumberInput,
    PasswordInput,
    RadioSelect,
    Select,
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


class KaraSelect(Select):
    template_name = "base/widgets/select.html"


class KaraNumberInput(NumberInput):
    template_name = "base/widgets/input.html"


class KaraCheckboxInput(CheckboxInput):
    template_name = "base/widgets/checkbox.html"


class KaraSearchInput(TextInput):
    input_type = "search"
    template_name = "base/widgets/search.html"


class StaticImageSelect(ChoiceWidget):
    template_name = "base/widgets/image_select.html"

    class Media:
        js = ["base/js/imageSelect.js"]

    def __init__(self, location, folder, attrs=None):
        # The current logic for retrieving the image target is temporary.
        # It may change later as the design will need to consider S3 integration.
        storage = default_storage.__class__(
            location=os.path.join(settings.STATIC_LOCATION, location)
        )
        _, files = storage.listdir(folder)
        choices = (("wedding_gifts/img/registry/" + file, None) for file in files)
        super().__init__(attrs=attrs, choices=choices)


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


class DropdownCheckboxSelectMultiple(CheckboxSelectMultiple):
    template_name = "base/widgets/dropdown/dropdown_checkbox_select_multiple.html"
