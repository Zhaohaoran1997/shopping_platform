from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ChangePasswordSerializer,
    UserAddressSerializer
)
from .models import UserAddress
from django.contrib import admin
from django.contrib import messages
from django.urls import reverse

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # 默认需要认证

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'login', 'logout']:
            return [permissions.AllowAny()]  # 这些操作允许未认证访问
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # 确保用户只能更新自己的信息
        if instance != request.user and not request.user.is_staff:
            raise permissions.PermissionDenied("您只能更新自己的信息")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # 确保用户只能更新自己的信息
        if instance != request.user and not request.user.is_staff:
            raise permissions.PermissionDenied("您只能更新自己的信息")
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': '请提供用户名和密码'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                response_data = {
                    'token': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                }
                return Response(response_data)
            else:
                return Response(
                    {'error': '密码错误'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        return Response({'message': '退出登录成功'})

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response({'message': '密码修改成功'})
            return Response(
                {'error': '原密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class UserAddressViewSet(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        # 确保用户只能访问自己的地址
        if user != self.request.user:
            return UserAddress.objects.none()
        return UserAddress.objects.filter(user=user)

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        # 确保用户只能创建自己的地址
        if user != self.request.user:
            raise permissions.PermissionDenied("您只能创建自己的地址")
        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # 确保用户只能更新自己的地址
        if instance.user != request.user:
            raise permissions.PermissionDenied("您只能更新自己的地址")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # 确保用户只能更新自己的地址
        if instance.user != request.user:
            raise permissions.PermissionDenied("您只能更新自己的地址")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 确保用户只能删除自己的地址
        if instance.user != request.user:
            raise permissions.PermissionDenied("您只能删除自己的地址")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def set_default(self, request, user_id=None, pk=None):
        address = self.get_object()
        # 确保用户只能设置自己的地址为默认
        if address.user != request.user:
            raise permissions.PermissionDenied("您只能设置自己的地址为默认")
        address.is_default = True
        address.save()
        return Response({'message': '设置默认地址成功'})

@admin.site.admin_view
def admin_disable_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, f'不能禁用超级管理员用户 {user.username}')
    else:
        user.is_active = False
        user.save()
        messages.success(request, f'用户 {user.username} 已禁用')
    return redirect(reverse('admin:users_user_changelist'))

@admin.site.admin_view
def admin_enable_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'用户 {user.username} 已启用')
    return redirect(reverse('admin:users_user_changelist'))

@admin.site.admin_view
def admin_reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    new_password = User.objects.make_random_password()
    user.set_password(new_password)
    user.save()
    messages.success(request, f'用户 {user.username} 的密码已重置为: {new_password}')
    return redirect(reverse('admin:users_user_changelist'))
