from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from .models import UserAddress

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'phone', 'code')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不匹配"})
        
        # 验证验证码
        email = attrs.get('email')
        code = attrs.get('code')
        cache_key = f'register_code_{email}'
        cached_code = cache.get(cache_key)
        
        if not cached_code or cached_code != code:
            raise serializers.ValidationError({"code": "验证码无效或已过期"})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('code')
        user = User.objects.create_user(**validated_data)
        # 删除验证码缓存
        cache.delete(f'register_code_{user.email}')
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "两次输入的密码不匹配"})
        return attrs

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ('id', 'receiver', 'phone', 'province', 'city', 'district', 'address', 'is_default', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("请输入有效的手机号码")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "两次输入的密码不匹配"})
        return attrs

class SendResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class SendRegisterCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True) 