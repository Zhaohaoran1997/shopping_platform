from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import User, UserAddress

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('email', 'phone')}),
        (_('权限'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def reset_password(self, request, queryset):
        for user in queryset:
            # 生成随机密码
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            messages.success(request, f'用户 {user.username} 的密码已重置为: {new_password}')
    reset_password.short_description = "重置选中用户的密码"

    actions = ['reset_password']

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'receiver', 'phone', 'province', 'city', 'district', 'is_default', 'created_at')
    list_filter = ('is_default', 'province', 'city', 'created_at')
    search_fields = ('user__username', 'receiver', 'phone', 'address')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
