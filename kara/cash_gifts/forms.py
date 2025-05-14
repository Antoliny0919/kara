from django.forms import RadioSelect
from django.utils.translation import gettext_lazy as _

from kara.base.forms import KaraModelForm

from .fields import UnitPriceField
from .models import CashGifts, CashGiftsRecordRepository


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


class CashGiftsForm(KaraModelForm):

    price = UnitPriceField(
        choices=[("1", 1), ("10000", 10000)],
        label=CashGifts._meta.get_field("price").verbose_name,
        initial={"select": "1"},
        help_text=_("Enter the amount of the cash gift received."),
    )

    class Meta:
        model = CashGifts
        fields = [
            "name",
            "price",
            "receipt_date",
        ]
        help_texts = {
            "name": _("Enter the name of the person who gave the cash gift."),
            "receipt_date": _("Enter the date the cash gift was received."),
        }
