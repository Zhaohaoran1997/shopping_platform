from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.html import format_html
from django.urls import path, reverse
from django.contrib.auth.decorators import user_passes_test
from .models import User, UserAddress

class UserAddressInline(admin.TabularInline):
    model = UserAddress
    extra = 1
    fields = ('receiver', 'phone', 'province', 'city', 'district', 'address', 'is_default')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active', 'created_at', 'get_actions')
    list_filter = ('is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)
    inlines = [UserAddressInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('email', 'phone')}),
        (_('权限'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('重要日期'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    def get_actions(self, obj):
        # 如果是请求对象，返回空字符串
        if hasattr(obj, 'method'):
            return ''
            
        # 如果是用户对象
        if not obj:
            return ''
            
        actions = []
        if obj.is_active:
            actions.append(
                format_html(
                    '<a class="button" style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;" href="{}">禁用</a>',
                    reverse('admin:admin-disable-user', args=[obj.id])
                )
            )
        else:
            actions.append(
                format_html(
                    '<a class="button" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;" href="{}">启用</a>',
                    reverse('admin:admin-enable-user', args=[obj.id])
                )
            )
        actions.append(
            format_html(
                '<a class="button" style="background-color: #007bff; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;" href="{}">重置密码</a>',
                reverse('admin:admin-reset-password', args=[obj.id])
            )
        )
        return ' | '.join(actions)
    get_actions.short_description = '操作'

    def get_urls(self):
        from . import views
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/disable/',
                user_passes_test(lambda u: u.is_staff)(views.admin_disable_user),
                name='admin-disable-user'
            ),
            path(
                '<int:user_id>/enable/',
                user_passes_test(lambda u: u.is_staff)(views.admin_enable_user),
                name='admin-enable-user'
            ),
            path(
                '<int:user_id>/reset-password/',
                user_passes_test(lambda u: u.is_staff)(views.admin_reset_password),
                name='admin-reset-password'
            ),
        ]
        return custom_urls + urls

    def reset_password(self, request, queryset):
        if not request.user.is_staff:
            messages.error(request, '您没有权限执行此操作')
            return
            
        for user in queryset:
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
    readonly_fields = ('created_at', 'updated_at')
