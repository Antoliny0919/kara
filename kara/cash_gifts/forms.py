from django.forms import RadioSelect
from django.utils.translation import gettext_lazy as _

from kara.base.forms import KaraModelForm

from .models import CashGiftsRecordRepository


class CashGiftsRecordRepositoryForm(KaraModelForm):

    class Meta:
        model = CashGiftsRecordRepository
        fields = [
            "side",
            "receiver",
            "receptionist",
            "wedding_date",
            "in_kind_gifts_allow",
        ]
        help_texts = {
            "receiver": _(
                "Please enter the name of the person receiving the cash gifts."
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
        labels = {"side": _("Select Groom's or Bride's Side")}
