from django import forms
from django.forms.widgets import RadioSelect, TextInput
from django.test import SimpleTestCase

from kara.base.forms import ConvertWidgetMixin, KaraWidgetMixin


class CustomRadioSelect(RadioSelect):
    pass


class CustomTextInput(TextInput):
    pass


class CustomWidgetMixin(ConvertWidgetMixin):
    widgets_map = {
        "TextInput": CustomTextInput,
        "RadioSelect": CustomRadioSelect,
    }


class CustomForm(CustomWidgetMixin, forms.Form):
    pass


class ParentForm(CustomForm):
    name = forms.CharField(max_length=128, required=True)
    type = forms.CharField(
        widget=RadioSelect(choices=[("F", "Father"), ("M", "Mother")])
    )


class KaraForm(KaraWidgetMixin, forms.Form):
    pass


class VotingLogForm(KaraForm):
    name = forms.CharField(label="name", max_length=64)
    voting_status = forms.BooleanField()
    voting_date = forms.DateField()


class ConvertWidgetMixinTest(SimpleTestCase):

    def test_convert_widget(self):
        form = ParentForm()
        case = zip(
            [field.field.widget for field in form], [CustomTextInput, CustomRadioSelect]
        )
        for widget, cls in case:
            self.assertTrue(isinstance(widget, cls))

    def test_preserve_attributes_from_before_widget(self):
        form = ParentForm()
        name_field = str(form["name"])
        self.assertIn("required", name_field)
        self.assertIn('maxlength="128"', name_field)
        type_field = str(form["type"])
        self.assertIn(
            '<input type="radio" name="type" value="F" required id="id_type_0">'
            "\n Father",
            type_field,
        )
        self.assertIn(
            '<input type="radio" name="type" value="M" required id="id_type_1">'
            "\n Mother",
            type_field,
        )


class KaraWidgetMixinTest(SimpleTestCase):

    def test_widget_have_label_value(self):
        form = VotingLogForm()
        name_widget = form["name"].field.widget
        self.assertIn("label", name_widget.attrs)
        self.assertEqual(name_widget.attrs["label"], "name")
