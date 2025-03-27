from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductSpecification, ProductReview
from apps.users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'level']

class ProductImageSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'order']

class ProductSpecificationSerializer(serializers.ModelSerializer):
    """商品规格序列化器"""
    class Meta:
        model = ProductSpecification
        fields = ['id', 'name', 'value']

class ProductReviewSerializer(serializers.ModelSerializer):
    """商品评价序列化器"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'username', 'rating', 'content', 'images', 'is_anonymous', 'created_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        username = validated_data.pop('username', None)
        if username:
            validated_data['user'] = User.objects.get(username=username)
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_id', 'description', 'price',
            'stock', 'sales', 'rating', 'review_count', 'is_active',
            'images', 'main_image', 'specifications', 'reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['sales', 'rating', 'review_count']

    def get_main_image(self, obj):
        """获取主图"""
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        return None

    def validate_category_id(self, value):
        """验证分类ID是否存在"""
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError('商品分类不存在')
        return value 