from django.contrib import admin
from .models import Coupon, UserCoupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'amount', 'min_amount', 'start_time', 'end_time', 'status']
    list_filter = ['type', 'status', 'start_time', 'end_time']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'type', 'amount', 'min_amount')
        }),
        ('时间设置', {
            'fields': ('start_time', 'end_time')
        }),
        ('状态信息', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )

@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon', 'status', 'created_at', 'used_at']
    list_filter = ['status', 'created_at', 'used_at']
    search_fields = ['user__username', 'user__email', 'coupon__name']
    readonly_fields = ['created_at', 'used_at']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('消费券信息', {
            'fields': ('coupon',)
        }),
        ('使用信息', {
            'fields': ('status', 'created_at', 'used_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'coupon')
