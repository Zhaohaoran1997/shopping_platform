from rest_framework import serializers
from .models import ReturnRequest, ReturnImage
from apps.orders.serializers import OrderSerializer
from apps.orders.models import Order, OrderItem
from apps.products.models import Product

class ReturnImageSerializer(serializers.ModelSerializer):
    """退换货图片序列化器"""
    class Meta:
        model = ReturnImage
        fields = ['id', 'image', 'created_at']
        read_only_fields = ['created_at']

class ReturnRequestSerializer(serializers.ModelSerializer):
    """退换货申请序列化器"""
    images = ReturnImageSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_number = serializers.CharField(source='order.order_no', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = ReturnRequest
        fields = [
            'id', 'order_number', 'product_name', 'product_image', 'product_price',
            'quantity', 'total_price', 'discount_amount', 'actual_amount',
            'type', 'type_display', 'reason', 'description', 'status',
            'status_display', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'status', 'created_at', 'updated_at', 'total_price',
            'discount_amount', 'actual_amount'
        ]

class ReturnRequestCreateSerializer(serializers.ModelSerializer):
    """退换货申请创建序列化器"""
    order_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = ReturnRequest
        fields = ['order_id', 'product_id', 'quantity', 'type', 'reason', 'description', 'images']

    def validate(self, data):
        """验证订单和商品"""
        print("Received data:", data)  # 添加调试日志
        order_id = data.get('order_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        user = self.context['request'].user

        try:
            order = Order.objects.get(id=order_id, user=user)
            if order.status != 3:  # 只有已完成的订单可以申请退换货
                raise serializers.ValidationError('只有已完成的订单可以申请退换货')
            
            # 验证商品是否属于该订单
            order_item = order.items.filter(product_id=product_id).first()
            if not order_item:
                raise serializers.ValidationError('该商品不属于此订单')
            
            # 验证退货数量是否超过购买数量
            if quantity > order_item.quantity:
                raise serializers.ValidationError(f'退货数量不能超过购买数量({order_item.quantity})')
            
            # 验证是否已经申请过退换货
            if ReturnRequest.objects.filter(order=order, product_id=product_id).exists():
                raise serializers.ValidationError('该商品已经申请过退换货')
            
            # 计算退货总价和实际退款金额
            total_price = order_item.price * quantity
            
            # 计算优惠比例
            if order.total_amount > 0:
                discount_ratio = order.discount_amount / order.total_amount
                discount_amount = total_price * discount_ratio
                actual_amount = total_price - discount_amount
            else:
                discount_amount = 0
                actual_amount = total_price
            
            data['total_price'] = total_price
            data['discount_amount'] = discount_amount
            data['actual_amount'] = actual_amount
            data['original_order'] = order  # 保存原订单对象，供创建时使用
            
            return data
        except Order.DoesNotExist:
            raise serializers.ValidationError('订单不存在')

    def create(self, validated_data):
        # 获取订单商品信息
        order_item = OrderItem.objects.get(
            order_id=validated_data['order_id'],
            product_id=validated_data['product_id']
        )
        
        # 计算退货总价
        total_price = order_item.price * validated_data.get('quantity', 1)
        
        # 创建退货请求
        return_request = ReturnRequest.objects.create(
            user=validated_data['user'],
            order=order_item.order,
            product=order_item.product,
            type=validated_data['type'],
            reason=validated_data['reason'],
            description=validated_data.get('description', ''),
            quantity=validated_data.get('quantity', 1),
            total_price=total_price
        )
        
        # 处理图片
        if 'images' in validated_data:
            for image_url in validated_data['images']:
                ReturnImage.objects.create(
                    return_request=return_request,
                    image_url=image_url
                )
        
        return return_request

class ReturnRequestDetailSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = ReturnRequest
        fields = [
            'id', 'order_number', 'product_name', 'product_image',
            'product_price', 'return_type', 'reason', 'description',
            'status', 'created_at', 'shipping_company', 'tracking_number'
        ]

class ShippingInfoSerializer(serializers.Serializer):
    shipping_company = serializers.ChoiceField(choices=[
        ('SF', '顺丰速运'),
        ('ZTO', '中通快递'),
        ('YTO', '圆通速递'),
        ('YD', '韵达快递')
    ])
    tracking_number = serializers.CharField(max_length=50)

class OrderListSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order_no')
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'created_at', 'status_display']

class ProductListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'image_url', 'price']

    def get_image_url(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image_url
        # 如果没有主图，返回第一张图片
        first_image = obj.images.first()
        return first_image.image_url if first_image else None 