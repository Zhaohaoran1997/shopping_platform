from rest_framework import serializers
from .models import Coupon, UserCoupon

class CouponSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'name', 'type', 'type_display', 'amount', 'min_amount',
            'start_time', 'end_time', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = UserCoupon
        fields = [
            'id', 'coupon', 'status', 'status_display',
            'created_at', 'used_at'
        ]
        read_only_fields = ['created_at', 'used_at']

class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'name', 'type', 'amount', 'min_amount',
            'start_time', 'end_time'
        ]

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError('结束时间必须晚于开始时间')
        return attrs 