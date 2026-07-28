from django.contrib import admin
from .models import *
from django.utils.html import format_html # Havola yaratish uchun kerak
# from .models import Buy
# Register your models here.
admin.site.register(Category)
admin.site.register(Sneakers)
# admin.site.register(Buy)
admin.site.register(Advertising)
admin.site.register(Register)

@admin.register(Buy)
class BuyAdmin(admin.ModelAdmin):
    # Admin paneldagi ro'yxatda ko'rinadigan ustunlar
    list_display = ('id', 'name', 'phone', 'product', 'size', 'how', 'show_map_link', 'status')
    
    # Statusni tezkor o'zgartirish uchun qulaylik
    list_editable = ('status',)
    
    # Qidiruv bo'limi
    search_fields = ('name', 'phone', 'email')

    # GRADUSLARNI LINKKA AYLANTIRUVCHI YANGI FUNKSIYA
    def show_map_link(self, obj):
        if obj.map and "," in obj.map:
            # Google Maps havolasini yaratish
            url = f"https://www.google.com/maps/search/?api=1&query={obj.map}"
            return format_html(
                '<a href="{}" target="_blank" style="color: #264b5d; font-weight: bold; text-decoration: underline;">'
                '📍 Xaritada ko\'rish ({})</a>', 
                url, obj.map
            )
        return obj.map
    
    # Admin paneldagi ustun nomi
    show_map_link.short_description = "Yetkazish manzili"