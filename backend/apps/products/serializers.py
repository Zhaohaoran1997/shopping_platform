from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductSpecification

class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'level', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['level', 'created_at', 'updated_at']

class ProductImageSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main', 'created_at']
        read_only_fields = ['created_at']

class ProductSpecificationSerializer(serializers.ModelSerializer):
    """商品规格序列化器"""
    class Meta:
        model = ProductSpecification
        fields = ['id', 'name', 'value', 'created_at']
        read_only_fields = ['created_at']

class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        source='images.image_url',
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'price', 'stock', 'sales', 'status', 'is_active',
            'created_at', 'updated_at', 'images', 'specifications',
            'image_urls'
        ]
        read_only_fields = ['sales', 'created_at', 'updated_at']

class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.URLField(),
        required=False
    )
    specifications = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'price', 'stock',
            'status', 'is_active', 'images', 'specifications'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        specifications_data = validated_data.pop('specifications', [])
        
        product = Product.objects.create(**validated_data)
        
        # Create product images
        for image_url in images_data:
            ProductImage.objects.create(
                product=product,
                image_url=image_url,
                is_main=not ProductImage.objects.filter(product=product).exists()
            )
        
        # Create product specifications
        for spec_data in specifications_data:
            ProductSpecification.objects.create(product=product, **spec_data)
        
        return product

    def validate_category(self, value):
        """验证分类是否存在"""
        try:
            Category.objects.get(id=value.id)
        except Category.DoesNotExist:
            raise serializers.ValidationError('商品分类不存在')
        return value 