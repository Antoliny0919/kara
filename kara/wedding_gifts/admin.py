from django.contrib import admin

from .models import GiftTag, WeddingGift, WeddingGiftRegistry


class WeddingGiftRegistryAdmin(admin.ModelAdmin):
    list_display = ["id", "side", "wedding_date"]


admin.site.register(WeddingGift)
admin.site.register(GiftTag)
admin.site.register(WeddingGiftRegistry, WeddingGiftRegistryAdmin)
