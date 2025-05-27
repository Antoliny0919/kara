import uuid

from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from kara.accounts.models import User


class WeddingGiftRegistry(models.Model):
    GROOM = "Groom"
    BRIDE = "Bride"
    SIDE = (
        (GROOM, _("Groom's side")),
        (BRIDE, _("Bride's side")),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wedding_gift_registries"
    )
    side = models.CharField(choices=SIDE, default=GROOM)
    receiver = models.CharField(
        max_length=64,
        help_text=(
            "This is the person who is getting married and receiving the wedding gift."
        ),
        verbose_name=_("receiver"),
    )
    receptionist = models.CharField(
        max_length=64,
        help_text="This is the person who recorded the wedding gift receipt details.",
        verbose_name=_("receptionist"),
    )
    wedding_date = models.DateField(verbose_name=_("wedding date"))
    updated_at = models.DateField(auto_now=True)
    in_kind_gifts_allow = models.BooleanField(
        default=True,
        help_text="Specifies whether to include the details of in-kind gift received.",
        verbose_name=_("include in-kind gifts"),
    )


class CashGift(models.Model):
    registry = models.ForeignKey(
        WeddingGiftRegistry,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=128, verbose_name=_("name"))
    price = models.PositiveIntegerField(verbose_name=_("price"))
    receipt_date = models.DateField(
        default=timezone.now, verbose_name=_("date of receipt")
    )
    tags = models.ManyToManyField(
        "GiftTag",
        blank=True,
        verbose_name=_("tags"),
    )

    class Meta:
        default_related_name = "cash_gifts"


class GiftTag(models.Model):
    name = models.CharField(max_length=64, verbose_name=_("name"))
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tags",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"), "owner", name="unique_lower_name_owner"
            )
        ]

    def __str__(self):
        return self.name
