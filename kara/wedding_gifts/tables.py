from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import (
    CharField,
    DateField,
    DateTimeField,
    ManyToManyField,
    TextField,
)
from django.template.defaultfilters import truncatewords
from django.utils.formats import date_format
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from kara.base.tables import Table, TableSearchForm
from kara.base.utils import get_contrast_color


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
        elif isinstance(field, (DateField, DateTimeField)):
            value = date_format(value)
        elif column in self.int_commas and isinstance(value, (int, float)):
            value = intcomma(value)
        elif isinstance(field, ManyToManyField) and column == "tags":
            # tags field renders all tags as HTML in a ul/li format.
            tags = value.all()
            tag_list_html = format_html_join(
                "\n",
                '<li style="background-color: {}; color: {};">{}</li>',
                (
                    (tag.hex_color, get_contrast_color(tag.hex_color), tag.name)
                    for tag in tags
                ),
            )
            value = format_html('<ul class="tags">\n{}\n</ul>', tag_list_html)
            return value
        return value


class CashGiftTable(GiftTable):
    columns = ["name", "price", "receipt_date", "tags"]


class InKindGiftTable(GiftTable):
    columns = ["name", "kind", "kind_detail", "price", "receipt_date", "tags"]


class GiftTagTable(Table):
    columns = ["name", "description", "hex_color"]
