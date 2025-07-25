from django.forms import RadioSelect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from kara.base.forms import KaraModelForm
from kara.base.widgets import StaticImageSelect

from .fields import UnitPriceField
from .models import CashGift, Gift, InKindGift, WeddingGiftRegistry
from .widgets import TagSelectWidget


class WeddingGiftRegistryForm(KaraModelForm):

    class Meta:
        model = WeddingGiftRegistry
        fields = [
            "cover_image",
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
            "cover_image": StaticImageSelect(
                location="wedding_gifts/static/wedding_gifts/img/",
                folder="registry",
                attrs={"help_text": _("Try selecting a featured image.")},
            ),
            "side": RadioSelect,
        }
        labels = {"side": _("Select Groom's or Bride's Side")}


class GiftForm(KaraModelForm):
    price = UnitPriceField(
        choices=[("1", 1), ("10000", 10000)],
        label=CashGift._meta.get_field("price").verbose_name,
        initial={"select": "1"},
    )

    class Meta:
        model = Gift
        fields = [
            "name",
            "price",
            "receipt_date",
            "tags",
        ]
        help_texts = {
            "name": _("Enter the name of the person who gave the wedding gift."),
            "receipt_date": _("Enter the date the wedding gift was received."),
            "tags": _("Add tags to categorize your gifts."),
        }
        widgets = {"tags": TagSelectWidget()}


class CashGiftForm(GiftForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].help_text = _(
            "Enter the amount of the cash gift received."
        )

    class Meta(GiftForm.Meta):
        model = CashGift


class InKindGiftForm(GiftForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].help_text = mark_safe(
            _(
                "Enter the price of the gift.<br>"
                "(It's okay if you're not sure of the exact amount, "
                "please provide an estimated value.)"
            )
        )

    class Meta(GiftForm.Meta):
        model = InKindGift
        fields = [
            "name",
            "kind",
            "kind_detail",
            "price",
            "receipt_date",
            "tags",
        ]
        help_texts = {
            **GiftForm.Meta.help_texts,
            "kind": _("What kind of gift did you receive?"),
            "kind_detail": _(
                "Do you know exactly which gift you received?" "If so, please enter it!"
            ),
        }
