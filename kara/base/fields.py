from django.forms.fields import ChoiceField, IntegerField, MultiValueField

from .widgets import UnitNumberInput


class UnitNumberField(MultiValueField):
    """
    Allows large numbers to be entered easily by selecting a unit.
    e.g. unit: 100, number: 100, result: 10000
    """

    widget_cls = UnitNumberInput

    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        fields = (
            ChoiceField(choices=choices),
            IntegerField(),
        )
        widget = self.widget_cls(attrs=attrs, choices=choices)
        super().__init__(
            fields=fields, widget=widget, require_all_fields=False, *args, **kwargs
        )

    def compress(self, data_list):
        result_value = int(data_list[0]) * int(data_list[1])
        return result_value
