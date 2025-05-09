from django.forms import RadioSelect
from django.utils.translation import gettext_lazy as _

from kara.base.forms import KaraModelForm

from .models import CashGiftsRecordRepository


class CashGiftsRecordRepositoryForm(KaraModelForm):

    class Meta:
        model = CashGiftsRecordRepository
        fields = [
            "side",
            "honoree",
            "receptionist",
            "wedding_date",
            "in_kind_gifts_allow",
        ]
        help_texts = {
            "honoree": _(
                "Please enter the name of the person getting married "
                "and receiving the cash gifts."
            ),
            "receptionist": _(
                "Please enter the name of the person who is recording "
                "the cash gifts details."
            ),
            "in_kind_gifts_allow": _("Please check to include in kind gifts details."),
        }
        widgets = {
            "side": RadioSelect,
        }
