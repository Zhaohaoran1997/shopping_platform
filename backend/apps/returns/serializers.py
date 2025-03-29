from rest_framework import serializers
from .models import ReturnRequest, ReturnImage
from apps.orders.serializers import OrderSerializer
from apps.orders.models import Order
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

    class Meta:
        model = ReturnRequest
        fields = [
            'id', 'order_number', 'product_name', 'product_image', 'product_price',
            'quantity', 'total_price', 'type', 'type_display', 'reason',
            'description', 'status', 'status_display', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at', 'total_price']

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
            
            # 计算退货总价
            data['total_price'] = order_item.price * quantity
            
            return data
        except Order.DoesNotExist:
            raise serializers.ValidationError('订单不存在')

    def create(self, validated_data):
        """创建退换货申请"""
        print("Validated data:", validated_data)  # 添加调试日志
        # 从 validated_data 中获取并移除 write_only 字段
        order_id = validated_data.pop('order_id', None)
        product_id = validated_data.pop('product_id', None)
        quantity = validated_data.pop('quantity', 1)
        total_price = validated_data.pop('total_price', 0)  # 获取计算好的总价
        images_data = validated_data.pop('images', [])
        
        print("Extracted order_id:", order_id)  # 添加调试日志
        print("Extracted product_id:", product_id)  # 添加调试日志
        print("Extracted quantity:", quantity)  # 添加调试日志
        print("Extracted total_price:", total_price)  # 添加调试日志
        
        if not order_id or not product_id:
            raise serializers.ValidationError('订单ID和商品ID不能为空')
        
        # 创建退换货申请
        return_request = ReturnRequest.objects.create(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,  # 添加总价
            **validated_data  # validated_data 中已经包含了 user
        )
        
        # 创建退换货图片
        for image_data in images_data:
            ReturnImage.objects.create(
                return_request=return_request,
                image=image_data
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