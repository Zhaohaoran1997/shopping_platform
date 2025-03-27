from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ReturnRequest
from .serializers import ReturnRequestSerializer, ReturnRequestCreateSerializer

# Create your views here.

class ReturnRequestViewSet(viewsets.ModelViewSet):
    """退换货申请视图集"""
    serializer_class = ReturnRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取用户的退换货申请列表"""
        queryset = ReturnRequest.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset.select_related('order')

    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'create':
            return ReturnRequestCreateSerializer
        return ReturnRequestSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消退换货申请"""
        return_request = self.get_object()
        if return_request.status != ReturnRequest.STATUS_CHOICES[0][0]:  # 待审核
            return Response(
                {'detail': '只有待审核的申请可以取消'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return_request.status = ReturnRequest.STATUS_CHOICES[4][0]  # 已取消
        return_request.save()

        return Response({'detail': '取消成功'})

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
