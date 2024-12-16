from django.contrib import admin
from .models import MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'available', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'available', 'restaurant')
    ordering = ('restaurant', 'name')

