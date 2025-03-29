from django.contrib import admin
from django.db import transaction
from django.utils.html import format_html
from .models import ReturnRequest, ReturnImage
from apps.orders.models import Order, OrderItem

class ReturnImageInline(admin.TabularInline):
    model = ReturnImage
    extra = 0
    readonly_fields = ['created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_order_number', 'get_product_name', 'type_display', 'status_display', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('order__order_no', 'product__name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'get_order_number', 'get_product_name', 'get_product_price', 
                      'get_total_price', 'get_discount_amount', 'get_actual_amount')
    fieldsets = (
        ('基本信息', {
            'fields': ('get_order_number', 'get_product_name', 'get_product_price', 'quantity', 'get_total_price')
        }),
        ('退换货信息', {
            'fields': ('type', 'reason', 'description', 'status')
        }),
        ('金额信息', {
            'fields': ('get_discount_amount', 'get_actual_amount')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        })
    )
    inlines = [ReturnImageInline]
    ordering = ['-created_at']

    def get_order_number(self, obj):
        return obj.order.order_no if obj.order else '-'
    get_order_number.short_description = '订单号'

    def get_product_name(self, obj):
        return obj.product.name if obj.product else '-'
    get_product_name.short_description = '商品名称'

    def get_product_price(self, obj):
        return obj.product.price if obj.product else '0.00'
    get_product_price.short_description = '商品单价'

    def get_total_price(self, obj):
        if obj.product:
            return obj.product.price * obj.quantity
        return '0.00'
    get_total_price.short_description = '退货总价'

    def get_discount_amount(self, obj):
        if obj.order:
            # 计算优惠金额（按原订单的优惠比例）
            discount_ratio = obj.order.discount_amount / obj.order.total_amount
            return obj.get_total_price() * discount_ratio
        return '0.00'
    get_discount_amount.short_description = '优惠金额'

    def get_actual_amount(self, obj):
        if obj.order:
            # 计算实际退款金额
            total_price = obj.get_total_price()
            discount_amount = obj.get_discount_amount()
            return total_price - discount_amount
        return '0.00'
    get_actual_amount.short_description = '实际退款金额'

    def type_display(self, obj):
        return obj.get_type_display()
    type_display.short_description = '退换货类型'

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = '状态'

    def save_model(self, request, obj, form, change):
        if change:  # 只在更新时处理
            # 获取原始对象
            original_obj = ReturnRequest.objects.get(pk=obj.pk)
            
            # 如果状态从待审核变为已通过，且是换货申请
            if (original_obj.status == 0 and obj.status == 1 and 
                obj.type == 2 and not obj.exchange_order):
                with transaction.atomic():
                    # 获取原订单信息
                    original_order = obj.order
                    original_order_item = OrderItem.objects.get(
                        order=original_order,
                        product=obj.product
                    )
                    
                    # 计算新订单的金额
                    # 获取原订单的优惠比例
                    original_discount_ratio = original_order.discount_amount / original_order.total_amount
                    
                    # 计算新订单的金额
                    new_total_amount = obj.product.price * obj.quantity
                    new_discount_amount = new_total_amount * original_discount_ratio
                    
                    # 创建新订单
                    new_order = Order.objects.create(
                        user=original_order.user,
                        order_no=f"EX{original_order.order_no}",  # 添加EX前缀表示换货订单
                        total_amount=new_total_amount,
                        discount_amount=new_discount_amount,
                        status=1,  # 待付款状态
                        shipping_address=original_order.shipping_address,
                        shipping_name=original_order.shipping_name,
                        shipping_phone=original_order.shipping_phone,
                        remark=f"换货订单 - 原订单号：{original_order.order_no}"
                    )
                    
                    # 创建新订单的商品项
                    OrderItem.objects.create(
                        order=new_order,
                        product=obj.product,
                        quantity=obj.quantity,
                        price=original_order_item.price,
                        total_price=new_total_amount
                    )
                    
                    # 更新退换货申请，关联新订单
                    obj.exchange_order = new_order
                    obj.save()
        
        super().save_model(request, obj, form, change)
    
    def images(self, obj):
        if obj.images.exists():
            return format_html(
                '<div style="display: flex; gap: 10px;">' +
                ''.join([
                    f'<img src="{img.image_url}" style="max-width: 100px; max-height: 100px; object-fit: cover;" />'
                    for img in obj.images.all()
                ]) +
                '</div>'
            )
        return '-'
    images.short_description = '问题图片'
