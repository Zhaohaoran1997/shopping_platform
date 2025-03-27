from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.cache import cache
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ChangePasswordSerializer,
    UserAddressSerializer, ResetPasswordSerializer, SendResetCodeSerializer,
    SendRegisterCodeSerializer
)
from .models import UserAddress

User = get_user_model()

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # 默认需要认证

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'login', 'send_reset_code', 'reset_password', 'send_register_code']:
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
                response = Response(response_data)
                # 设置 cookie
                response.set_cookie(
                    'access_token',
                    str(refresh.access_token),
                    httponly=True,
                    secure=False,  # 开发环境设为 False，生产环境应该设为 True
                    samesite='Lax'
                )
                # 登录用户
                from django.contrib.auth import login
                login(request, user)
                return response
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
        from django.contrib.auth import logout
        logout(request)
        response = Response({'message': '退出登录成功'})
        response.delete_cookie('access_token')
        return response

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

    @action(detail=False, methods=['post'])
    def send_reset_code(self, request):
        serializer = SendResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                code = generate_verification_code()
                # 将验证码存入缓存，设置5分钟过期
                cache_key = f'reset_password_code_{email}'
                cache.set(cache_key, code, 300)  # 5分钟过期
                
                # 发送验证码邮件
                subject = '重置密码验证码'
                message = f'您的验证码是：{code}，5分钟内有效。'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]
                
                send_mail(subject, message, from_email, recipient_list)
                return Response({'message': '验证码已发送到您的邮箱'})
            except User.DoesNotExist:
                return Response(
                    {'error': '该邮箱未注册'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            
            # 验证验证码
            cache_key = f'reset_password_code_{email}'
            cached_code = cache.get(cache_key)
            
            if not cached_code or cached_code != code:
                return Response(
                    {'error': '验证码无效或已过期'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                # 删除验证码缓存
                cache.delete(cache_key)
                return Response({'message': '密码重置成功'})
            except User.DoesNotExist:
                return Response(
                    {'error': '用户不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_register_code(self, request):
        serializer = SendRegisterCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # 检查邮箱是否已注册
            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': '该邮箱已被注册'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            code = generate_verification_code()
            # 将验证码存入缓存，设置5分钟过期
            cache_key = f'register_code_{email}'
            cache.set(cache_key, code, 300)  # 5分钟过期
            
            # 发送验证码邮件
            subject = '注册验证码'
            message = f'您的验证码是：{code}，5分钟内有效。'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list)
            return Response({'message': '验证码已发送到您的邮箱'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
