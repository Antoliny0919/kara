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


class Gift(models.Model):
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
        abstract = True


class CashGift(Gift):

    class Meta:
        default_related_name = "cash_gifts"


class InKindGift(Gift):
    KIND_CHOICES = [
        ("appliance", _("Appliance")),
        ("kitchenware", _("Kitchenware")),
        ("furniture", _("Furniture")),
        ("decor", _("Decor")),
        ("bedding", _("Bedding")),
        ("food_or_drink", _("Food or Drink")),
        ("daily_goods", _("Daily Goods")),
        ("other", _("Other")),
    ]
    kind = models.CharField(
        choices=KIND_CHOICES, default="appliance", verbose_name=_("Gift Kind")
    )
    kind_detail = models.CharField(
        max_length=128, null=True, verbose_name=_("Gift Detail")
    )

    class Meta:
        default_related_name = "in_kind_gifts"
        # kind must have a detail when it is set to "other"
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(kind__exact="other")
                | models.Q(kind_detail__isnull=False),
                name="kind_other_require_detail",
            )
        ]
        verbose_name = _("In-kind gift")
        verbose_name_plural = _("In-kind gifts")


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
