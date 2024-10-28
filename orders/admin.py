from django.contrib import admin
from .models import Payment, Order, OrderProduct,Deliverer
from django.utils.html import format_html


# class OrderProdcutInline(admin.TabularInline):
#     # def thumbnail(self, object): 'thumbnail',
#     #     return format_html('<img src="{}" width="75" height="110">'.format(object.product.image.url))
#     # thumbnail.short_description = 'Product Picture'
#     model = OrderProduct
#     readonly_fields = ['product','variations','product_price', 'quantity','user','payment',    'ordered',  ]
#     extra = 0

class OrderProdcutInline(admin.TabularInline):
    def thumbnail(self, object):
        return format_html('<img style="border-radius:10px; width:100px; height:100px" src="{}">'.format(object.product.image.url))
    thumbnail.short_description = 'Product Picture'
    model = OrderProduct
    readonly_fields = ['thumbnail', 'product', 'variations', 'product_price', 'quantity', 'user', 'payment', 'ordered']
    extra = 0
    
admin.site.register(Payment)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'phone', 'order_total', 'status', 'is_ordered', 'deliverer']
    list_filter = ['is_ordered', 'status']
    list_per_page = 20
    inlines = [OrderProdcutInline]
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_editable = ['deliverer']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['order_number', 'full_name', 'email', 'phone', 'order_total', 'status', 'is_ordered']
        return []


admin.site.register(OrderProduct)


@admin.register(Deliverer)
class DelivererAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number', 'address']
    search_fields = ['user__first_name', 'user__last_name', 'phone_number', 'address']
    list_filter = ['user__is_active']
    list_per_page = 20

    def full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    full_name.short_description = 'Full Name'

