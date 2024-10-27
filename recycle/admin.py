from django.contrib import admin
from .models import DropPoint, RecycledItem
import admin_thumbnails


@admin.register(DropPoint)
class DropPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'description']

@admin.register(RecycledItem)
class RecycledItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'drop_point', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'drop_point']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']  
    search_fields = ['name', 'user__username'] 

    inlines = []  

