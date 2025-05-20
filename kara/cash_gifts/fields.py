from kara.base.fields import UnitNumberField
from kara.base.widgets import UnitNumberInput


class UnitPriceInput(UnitNumberInput):
    template_name = "cash_gifts/widgets/unit_price_input.html"


class UnitPriceField(UnitNumberField):
    widget_cls = UnitPriceInput
