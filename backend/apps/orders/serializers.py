from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'price', 'quantity', 'total_price']

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_name', 'shipping_phone', 
                 'shipping_province', 'shipping_city', 'shipping_district', 
                 'shipping_address_detail']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'total_amount', 'status', 'status_display',
                 'shipping_address', 'shipping_name', 'shipping_phone',
                 'shipping_province', 'shipping_city', 'shipping_district',
                 'shipping_address_detail', 'shipping_no', 'payment_method',
                 'created_at', 'updated_at', 'items']
        read_only_fields = ['order_no', 'total_amount', 'status', 'payment_method',
                          'created_at', 'updated_at'] 