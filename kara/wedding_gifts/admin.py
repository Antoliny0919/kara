from django.contrib import admin

from .models import CashGift, WeddingGiftRegistry


class WeddingGiftRegistryAdmin(admin.ModelAdmin):
    list_display = ["id", "side", "wedding_date"]


admin.site.register(CashGift)
admin.site.register(WeddingGiftRegistry, WeddingGiftRegistryAdmin)
