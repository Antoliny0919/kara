from django.contrib import admin

from .models import CashGifts, CashGiftsRecordRepository


class CashGiftsRecordRepositoryAdmin(admin.ModelAdmin):
    list_display = ["id", "side", "wedding_date"]


admin.site.register(CashGifts)
admin.site.register(CashGiftsRecordRepository, CashGiftsRecordRepositoryAdmin)
