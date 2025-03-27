from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    """购物车商品序列化器"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'selected', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_total_price(self, obj):
        """计算商品总价"""
        return obj.product.price * obj.quantity

    def validate_product_id(self, value):
        """验证商品ID是否存在"""
        try:
            from apps.products.models import Product
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value

class CartSerializer(serializers.ModelSerializer):
    """购物车序列化器"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_total_price(self, obj):
        """计算购物车总价"""
        return sum(item.product.price * item.quantity for item in obj.items.filter(selected=True)) 