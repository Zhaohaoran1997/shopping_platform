from django.contrib import admin
from .models import ReturnRequest, ReturnImage

class ReturnImageInline(admin.TabularInline):
    model = ReturnImage
    extra = 0
    readonly_fields = ['created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'type', 'status', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['order__order_no', 'user__username', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ReturnImageInline]
    ordering = ['-created_at']
