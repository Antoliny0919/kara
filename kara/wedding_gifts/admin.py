from django.contrib import admin

from .models import CashGift, GiftTag, WeddingGiftRegistry


class WeddingGiftRegistryAdmin(admin.ModelAdmin):
    list_display = ["id", "side", "wedding_date"]


admin.site.register(CashGift)
admin.site.register(GiftTag)
admin.site.register(WeddingGiftRegistry, WeddingGiftRegistryAdmin)
