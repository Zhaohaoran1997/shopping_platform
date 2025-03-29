from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from .models import ReturnRequest
from .serializers import (
    ReturnRequestSerializer,
    ReturnRequestDetailSerializer,
    OrderListSerializer,
    ShippingInfoSerializer,
    ProductListSerializer
)
from apps.orders.models import Order
from apps.products.models import Product
from rest_framework.pagination import PageNumberPagination

# Create your views here.

class ReturnRequestViewSet(viewsets.ModelViewSet):
    """退换货申请视图集"""
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """根据不同的操作使用不同的序列化器"""
        if self.action == 'create':
            from .serializers import ReturnRequestCreateSerializer
            return ReturnRequestCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        """获取用户的退换货申请列表"""
        queryset = ReturnRequest.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset.select_related('order')

    def perform_create(self, serializer):
        print("Request data:", self.request.data)  # 添加调试日志
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消退换货申请"""
        return_request = self.get_object()
        if return_request.status != 'pending':
            return Response(
                {'error': '只能取消待处理的申请'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return_request.status = 'cancelled'
        return_request.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取退换货申请进度"""
        return_request = self.get_object()
        return Response({
            'status': return_request.status,
            'status_display': return_request.get_status_display(),
            'created_at': return_request.created_at,
            'updated_at': return_request.updated_at
        })

class ReturnRequestDetailViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReturnRequestDetailSerializer

    def retrieve(self, request, pk=None):
        return_request = get_object_or_404(ReturnRequest, pk=pk, user=request.user)
        serializer = self.serializer_class(return_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_shipping(self, request, pk=None):
        return_request = get_object_or_404(ReturnRequest, pk=pk, user=request.user)
        if return_request.status != 'approved':
            return Response(
                {'error': '只能为已通过的申请提交物流信息'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ShippingInfoSerializer(data=request.data)
        if serializer.is_valid():
            return_request.shipping_company = serializer.validated_data['shipping_company']
            return_request.tracking_number = serializer.validated_data['tracking_number']
            return_request.status = 'shipped'
            return_request.save()
            return Response({'status': 'success'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReturnRequestImageUploadView(viewsets.ViewSet):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        if 'image' not in request.FILES:
            return Response(
                {'error': '没有上传文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image = request.FILES['image']
        # 这里需要实现图片上传到存储的逻辑
        # 可以使用 Django Storage 或其他存储服务
        
        return Response({
            'url': '图片URL',  # 替换为实际的图片URL
            'status': 'success'
        })

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class OrderListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Order.objects.filter(
            user=self.request.user,
            status=3  # 只显示已完成的订单
        )
        
        # 添加搜索功能
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(order_no__icontains=search)
        
        return queryset.order_by('-created_at')

    @action(detail=True)
    def products(self, request, pk=None):
        """获取订单中的商品列表"""
        order = self.get_object()
        # 获取订单中的商品，并排除已经申请过退换货的商品
        products = Product.objects.filter(
            orderitem__order=order
        ).exclude(
            id__in=ReturnRequest.objects.filter(
                order=order,
                status__in=[0, 1]  # 排除待审核和已同意的申请
            ).values_list('product_id', flat=True)
        ).distinct()
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
