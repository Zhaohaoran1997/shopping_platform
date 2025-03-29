from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductImage, ProductSpecification
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductCreateSerializer,
    ProductImageSerializer,
    ProductSpecificationSerializer
)

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filter by category
        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
            
        max_price = self.request.query_params.get('max_price', None)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        # Filter by is_active
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Search by name or description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # Order by
        order_by = self.request.query_params.get('order_by', '-created_at')
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        product = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Product.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        product.status = new_status
        product.save()
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProductImage.objects.all()
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    @action(detail=True, methods=['post'])
    def set_main(self, request, pk=None):
        image = self.get_object()
        # Set all other images of the same product to not main
        ProductImage.objects.filter(product=image.product).update(is_main=False)
        image.is_main = True
        image.save()
        serializer = self.get_serializer(image)
        return Response(serializer.data)

class ProductSpecificationViewSet(viewsets.ModelViewSet):
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProductSpecification.objects.all()
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
