from django.forms import RadioSelect
from django.utils.translation import gettext_lazy as _

from kara.base.forms import KaraModelForm

from .fields import UnitPriceField
from .models import WeddingGift, WeddingGiftRegistry


class WeddingGiftRegistryForm(KaraModelForm):

    class Meta:
        model = WeddingGiftRegistry
        fields = [
            "side",
            "receiver",
            "receptionist",
            "wedding_date",
        ]
        help_texts = {
            "receiver": _(
                "Please enter the name of the person receiving the wedding gift."
            ),
            "receptionist": _(
                "Please enter the name of the person who is recording "
                "the wedding gift details."
            ),
        }
        widgets = {
            "side": RadioSelect,
        }
        labels = {"side": _("Select Groom's or Bride's Side")}


class WeddingGiftForm(KaraModelForm):

    price = UnitPriceField(
        choices=[("1", 1), ("10000", 10000)],
        label=WeddingGift._meta.get_field("price").verbose_name,
        initial={"select": "1"},
        help_text=_("Enter the amount of the wedding gift received."),
    )

    class Meta:
        model = WeddingGift
        fields = [
            "name",
            "price",
            "receipt_date",
        ]
        help_texts = {
            "name": _("Enter the name of the person who gave the wedding gift."),
            "receipt_date": _("Enter the date the wedding gift was received."),
        }
