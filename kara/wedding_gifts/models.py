import uuid

from django.db import models
from django.db.models import CheckConstraint, Q
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


class WeddingGift(models.Model):
    CASH = "cash"
    NON_CASH = "non_cash"
    KIND_CHOICES = [
        (CASH, _("Cash")),
        (NON_CASH, _("Non-cash")),
    ]

    registry = models.ForeignKey(
        WeddingGiftRegistry,
        on_delete=models.CASCADE,
        related_name="wedding_gifts",
    )
    name = models.CharField(max_length=128, verbose_name=_("name"))
    kind = models.CharField(choices=KIND_CHOICES)
    non_cash_detail = models.CharField(max_length=128, blank=True, null=True)
    price = models.PositiveIntegerField(verbose_name=_("price"))
    receipt_date = models.DateField(
        default=timezone.now, verbose_name=_("date of receipt")
    )
    tags = models.ManyToManyField(
        "GiftTag",
        blank=True,
        related_name="wedding_gifts",
        verbose_name=_("tags"),
    )

    class Meta:
        constraints = [
            CheckConstraint(
                condition=Q(kind="cash"),
                check=Q(non_cash_detail__isnull=True),
                name="cash_no_detail",
            ),
        ]


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
