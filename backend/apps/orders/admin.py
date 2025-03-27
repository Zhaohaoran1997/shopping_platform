from django.contrib import admin
from .models import Order, OrderItem
from django.utils import timezone

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_image', 'price', 'quantity', 'total_price', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'user', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_no', 'user__username', 'user__email', 'shipping_name', 'shipping_phone']
    readonly_fields = ['order_no', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('order_no', 'user', 'total_amount', 'discount_amount', 'status')
        }),
        ('收货信息', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_province', 'shipping_city', 
                      'shipping_district', 'shipping_address_detail')
        }),
        ('物流信息', {
            'fields': ('shipping_no', 'shipping_company', 'shipping_time')
        }),
        ('支付信息', {
            'fields': ('payment_method', 'payment_no', 'payment_time')
        }),
        ('其他信息', {
            'fields': ('complete_time', 'created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def save_model(self, request, obj, form, change):
        if not change:  # 如果是新建订单
            obj.order_no = f'ORDER{timezone.now().strftime("%Y%m%d%H%M%S")}{obj.user.id}'
        super().save_model(request, obj, form, change)