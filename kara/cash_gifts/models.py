import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from kara.accounts.models import User


class CashGiftsRecordRepository(models.Model):
    GROOM = "Groom"
    BRIDE = "Bride"
    SIDE = (
        (GROOM, _("Groom's side")),
        (BRIDE, _("Bride's side")),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cash_gifts_record_repository"
    )
    side = models.CharField(choices=SIDE, default=GROOM)
    receiver = models.CharField(
        max_length=64,
        help_text=(
            "This is the person who is getting married and receiving the cash gifts."
        ),
        verbose_name=_("Receiver"),
    )
    receptionist = models.CharField(
        max_length=64,
        help_text="This is the person who recorded the cash gifts receipt details.",
        verbose_name=_("Receptionist"),
    )
    wedding_date = models.DateField(verbose_name=_("Wedding Date"))
    updated_at = models.DateField(auto_now=True)
    in_kind_gifts_allow = models.BooleanField(
        default=True,
        help_text="Specifies whether to include the details of in-kind gifts received.",
        verbose_name=_("Include In-Kind Gifts"),
    )


class CashGifts(models.Model):
    repository = models.ForeignKey(
        CashGiftsRecordRepository,
        on_delete=models.CASCADE,
        related_name="cash_gift_records",
    )
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    price = models.PositiveIntegerField(verbose_name=_("Price"))
    receipt_date = models.DateField(
        default=timezone.now, verbose_name=_("Date of Receipt")
    )
