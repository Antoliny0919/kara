from django.contrib import admin

from .models import CashGift, GiftTag, InKindGift, WeddingGiftRegistry


class WeddingGiftRegistryAdmin(admin.ModelAdmin):
    list_display = ["id", "side", "wedding_date"]


admin.site.register(CashGift)
admin.site.register(GiftTag)
admin.site.register(InKindGift)
admin.site.register(WeddingGiftRegistry, WeddingGiftRegistryAdmin)
