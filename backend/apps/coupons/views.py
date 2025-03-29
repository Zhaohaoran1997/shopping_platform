from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db import transaction
from .models import Coupon, UserCoupon
from .serializers import CouponSerializer, UserCouponSerializer, CouponCreateSerializer

# Create your views here.

class CouponViewSet(viewsets.ModelViewSet):
    """消费券管理"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """根据操作设置不同的权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CouponCreateSerializer
        return CouponSerializer

    def get_queryset(self):
        queryset = Coupon.objects.all()
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """领取消费券"""
        coupon = self.get_object()
        now = timezone.now()

        # 检查消费券是否可用
        if coupon.status != 1:
            return Response(
                {'detail': '消费券不可用'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if now < coupon.start_time or now > coupon.end_time:
            return Response(
                {'detail': '消费券不在有效期内'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查用户是否已领取
        if UserCoupon.objects.filter(user=request.user, coupon=coupon).exists():
            return Response(
                {'detail': '您已领取过该消费券'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建用户消费券
        UserCoupon.objects.create(user=request.user, coupon=coupon)
        return Response({'detail': '领取成功'})

class UserCouponViewSet(viewsets.ReadOnlyModelViewSet):
    """用户消费券"""
    serializer_class = UserCouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = UserCoupon.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset.select_related('coupon')

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """使用消费券"""
        user_coupon = self.get_object()
        try:
            user_coupon.use()
            return Response({'detail': '使用成功'})
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
