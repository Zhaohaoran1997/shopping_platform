from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('product_name', 'product_image', 'price', 'total_price', 'created_at')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'user', 'total_amount', 'get_status_display', 'payment_method', 'created_at', 'get_actions')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_no', 'user__username', 'shipping_name', 'shipping_phone')
    readonly_fields = ('order_no', 'created_at', 'updated_at', 'get_status_display')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('order_no', 'user', 'total_amount', 'status', 'payment_method', 'created_at', 'updated_at')
        }),
        ('收货信息', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_province', 'shipping_city', 
                      'shipping_district', 'shipping_address_detail', 'shipping_no')
        }),
    )

    def get_actions(self, obj):
        # 如果是请求对象，返回空字符串
        if hasattr(obj, 'method'):
            return ''
            
        # 如果是订单对象
        if not obj:
            return ''
            
        if obj.status == 0:  # 待付款
            return format_html(
                '<a class="button" style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;" href="{}">取消订单</a>',
                reverse('admin:admin-cancel-order', args=[obj.id])
            )
        elif obj.status == 1:  # 待发货
            return format_html(
                '<a class="button" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;" href="{}">发货</a>',
                reverse('admin:admin-ship-order', args=[obj.id])
            )
        return '-'
    get_actions.short_description = '操作'

    def get_urls(self):
        from django.urls import path
        from . import views
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/cancel/', views.admin_cancel_order, name='admin-cancel-order'),
            path('<int:order_id>/ship/', views.admin_ship_order, name='admin-ship-order'),
        ]
        return custom_urls + urls

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__order_no', 'product_name')
    readonly_fields = ('product_name', 'product_image', 'price', 'total_price', 'created_at')
    ordering = ('-created_at',)