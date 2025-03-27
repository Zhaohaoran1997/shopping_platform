from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.conf import settings
from django.db import models
from .models import Category, Product, ProductImage, ProductSpecification, ProductReview
from .serializers import (
    CategorySerializer, ProductSerializer, ProductImageSerializer,
    ProductSpecificationSerializer, ProductReviewSerializer
)

# Create your views here.

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """商品分类视图集"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        """获取分类列表（带缓存）"""
        cache_key = 'category_list'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=3600)  # 缓存1小时
            return response
        return Response(cached_data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """商品视图集"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price', 'rating']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sales', 'rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """获取商品列表"""
        queryset = super().get_queryset()
        
        # 价格区间筛选
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # 分类筛选
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 搜索优化：添加权重排序
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.annotate(
                search_rank=models.Case(
                    models.When(name__icontains=search, then=3),
                    models.When(description__icontains=search, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ).order_by('-search_rank')
        
        return queryset

    def list(self, request, *args, **kwargs):
        """获取商品列表（带缓存）"""
        cache_key = f'product_list_{request.query_params}'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=300)  # 缓存5分钟
            return response
        return Response(cached_data)

    def get_object(self):
        """获取商品详情（带缓存）"""
        obj = super().get_object()
        cache_key = f'product_detail_{obj.id}'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            serializer = self.get_serializer(obj)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=3600)  # 缓存1小时
        return obj

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """获取商品评价列表（带分页）"""
        product = self.get_object()
        reviews = product.reviews.all()
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ProductReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def specifications(self, request, pk=None):
        """获取商品规格列表（带缓存）"""
        product = self.get_object()
        cache_key = f'product_specifications_{product.id}'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            specifications = product.specifications.all()
            serializer = ProductSpecificationSerializer(specifications, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=3600)  # 缓存1小时
        return Response(cached_data)

class ProductReviewViewSet(viewsets.ModelViewSet):
    """商品评价视图集"""
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        """获取评价列表"""
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        """创建评价"""
        product_id = self.request.data.get('product_id')
        if not product_id:
            raise serializers.ValidationError('商品ID不能为空')
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        
        # 创建评价
        serializer.save(product=product)
        
        # 清除相关缓存
        cache.delete(f'product_detail_{product_id}')
        cache.delete(f'product_list_{self.request.query_params}')
