from django.conf import settings
from django.utils.translation import gettext_lazy as _

from kara.base.tables import Table, TableSearchForm


class CashGiftSearchForm(TableSearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[settings.SEARCH_VAR].help_text = _(
            "Looking for someone? Enter a name to find records that match it exactly."
        )


class CashGiftTable(Table):
    search_fields = ["name__iexact"]
    search_form_class = CashGiftSearchForm
