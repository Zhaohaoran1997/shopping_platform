from rest_framework import serializers
from .models import ReturnRequest, ReturnImage
from apps.orders.serializers import OrderSerializer

class ReturnImageSerializer(serializers.ModelSerializer):
    """退换货图片序列化器"""
    class Meta:
        model = ReturnImage
        fields = ['id', 'image', 'created_at']
        read_only_fields = ['created_at']

class ReturnRequestSerializer(serializers.ModelSerializer):
    """退换货申请序列化器"""
    order = OrderSerializer(read_only=True)
    images = ReturnImageSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ReturnRequest
        fields = [
            'id', 'order', 'type', 'type_display', 'reason', 'status', 'status_display',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

class ReturnRequestCreateSerializer(serializers.ModelSerializer):
    """退换货申请创建序列化器"""
    order_id = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = ReturnRequest
        fields = ['order_id', 'type', 'reason', 'images']

    def validate_order_id(self, value):
        """验证订单ID是否存在且属于当前用户"""
        try:
            from apps.orders.models import Order
            order = Order.objects.get(id=value, user=self.context['request'].user)
            if order.status not in [3]:  # 只有已完成的订单可以申请退换货
                raise serializers.ValidationError('只有已完成的订单可以申请退换货')
        except Order.DoesNotExist:
            raise serializers.ValidationError('订单不存在')
        return value

    def create(self, validated_data):
        """创建退换货申请"""
        order_id = validated_data.pop('order_id')
        images_data = validated_data.pop('images', [])
        
        # 创建退换货申请
        return_request = ReturnRequest.objects.create(
            order_id=order_id,
            user=self.context['request'].user,
            **validated_data
        )
        
        # 创建退换货图片
        for image_data in images_data:
            ReturnImage.objects.create(
                return_request=return_request,
                image=image_data
            )
        
        return return_request 