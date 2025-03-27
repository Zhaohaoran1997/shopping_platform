from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('product_name', 'product_image', 'price', 'total_price', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'user', 'total_amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_no', 'user__username', 'shipping_name', 'shipping_phone')
    readonly_fields = ('order_no', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__order_no', 'product_name')
    readonly_fields = ('product_name', 'product_image', 'price', 'total_price', 'created_at')
    ordering = ('-created_at',)