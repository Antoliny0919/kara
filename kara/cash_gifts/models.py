from django.db import models

from kara.accounts.models import User


class CashGiftsRecordRepository(models.Model):
    GROOM = "Groom"
    BRIDE = "Bride"
    SIDE = (
        (GROOM, "Groom's side"),
        (BRIDE, "Bride's side"),
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cash_gifts_record_repository"
    )
    side = models.CharField(choices=SIDE, default=GROOM)
    honoree = models.CharField(
        max_length=64,
        help_text=(
            "This is the person who is getting married " "and receiving the cash gifts."
        ),
    )
    receptionist = models.CharField(
        max_length=64,
        help_text="This is the person who recorded the cash gifts receipt details.",
    )
    wedding_date = models.DateField()
    updated_at = models.DateField(auto_now=True)
    in_kind_gifts_allow = models.BooleanField(
        default=True,
        help_text="Specifies whether to include the details of in kind gifts received.",
    )
