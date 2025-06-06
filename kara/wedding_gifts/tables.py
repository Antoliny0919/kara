from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import CharField, TextField
from django.template.defaultfilters import truncatewords
from django.utils.translation import gettext_lazy as _

from kara.base.tables import Table, TableSearchForm


class CashGiftSearchForm(TableSearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[settings.SEARCH_VAR].help_text = _(
            "Looking for someone? Enter a name to find records that match it exactly."
        )


class GiftTable(Table):
    search_fields = ["name__iexact"]
    search_form_class = CashGiftSearchForm
    int_commas = ["price"]
    ordering = ["price", "receipt_date"]

    def display_for_value(self, obj, column):
        field = obj.__class__._meta.get_field(column)
        value = super().display_for_value(obj, column)
        if isinstance(field, CharField) and field.choices is not None:
            value = getattr(obj, f"get_{column}_display")()
        elif isinstance(field, (CharField, TextField)):
            value = truncatewords(value, 8)
        elif column in self.int_commas and isinstance(value, (int, float)):
            value = intcomma(value)
        return value


class CashGiftTable(GiftTable):
    columns = ["name", "price", "receipt_date"]


class InKindGiftTable(GiftTable):
    columns = ["name", "kind", "kind_detail", "price", "receipt_date"]
