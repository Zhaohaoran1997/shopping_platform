from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer
from apps.users.models import UserAddress
from apps.coupons.models import UserCoupon

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_name = serializers.CharField(read_only=True)
    product_image = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'price', 'quantity', 'total_price']

class OrderCreateSerializer(serializers.ModelSerializer):
    address_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = Order
        fields = ['address_id', 'coupon_id', 'payment_method', 'remark']
        
    def validate(self, attrs):
        # 验证地址是否存在
        try:
            address = UserAddress.objects.get(id=attrs['address_id'], user=self.context['request'].user)
            # 将地址信息添加到订单数据中
            attrs['shipping_name'] = address.receiver
            attrs['shipping_phone'] = address.phone
            attrs['shipping_province'] = address.province
            attrs['shipping_city'] = address.city
            attrs['shipping_district'] = address.district
            attrs['shipping_address_detail'] = address.address
        except UserAddress.DoesNotExist:
            raise serializers.ValidationError('收货地址不存在')
            
        # 验证优惠券
        if attrs.get('coupon_id'):
            try:
                user_coupon = UserCoupon.objects.get(
                    id=attrs['coupon_id'],
                    user=self.context['request'].user,
                    status=0  # 未使用
                )
                attrs['coupon'] = user_coupon.coupon
            except UserCoupon.DoesNotExist:
                raise serializers.ValidationError('优惠券不存在或已使用')
                
        return attrs

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    shipping_address = serializers.IntegerField(source='shipping_address_id', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'total_amount', 'status', 'status_display',
            'shipping_address', 'shipping_name', 'shipping_phone',
            'shipping_province', 'shipping_city', 'shipping_district',
            'shipping_address_detail', 'shipping_no', 'payment_method',
            'payment_method_display', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['order_no', 'total_amount', 'status', 'payment_method',
                          'created_at', 'updated_at'] 