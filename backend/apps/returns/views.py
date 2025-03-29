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
    ShippingInfoSerializer
)
from apps.orders.models import Order
from apps.products.models import Product

# Create your views here.

class ReturnRequestViewSet(viewsets.ModelViewSet):
    """退换货申请视图集"""
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """获取用户的退换货申请列表"""
        queryset = ReturnRequest.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset.select_related('order')

    def perform_create(self, serializer):
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

class OrderListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status='completed'  # 只显示已完成的订单
        )

    @action(detail=True)
    def products(self, request, pk=None):
        order = self.get_object()
        products = Product.objects.filter(order_items__order=order)
        serializer = OrderListSerializer(products, many=True)
        return Response(serializer.data)
