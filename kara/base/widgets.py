from django.forms import TextInput
from django.forms.widgets import (
    CheckboxInput,
    EmailInput,
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
