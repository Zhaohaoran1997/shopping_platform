from django.contrib import admin
from .models import Category, Product, ProductImage, ProductSpecification

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """商品分类管理"""
    list_display = ['name', 'parent', 'level', 'is_active', 'created_at']
    list_filter = ['is_active', 'level']
    search_fields = ['name']
    ordering = ['level', 'id']

class ProductImageInline(admin.TabularInline):
    """商品图片内联"""
    model = ProductImage
    extra = 1
    fields = ['image', 'is_main']

class ProductSpecificationInline(admin.TabularInline):
    """商品规格内联"""
    model = ProductSpecification
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """商品管理"""
    list_display = ['name', 'category', 'price', 'stock', 'sales', 'is_active', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    inlines = [ProductImageInline, ProductSpecificationInline]
    readonly_fields = ['sales']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'description', 'price', 'stock', 'is_active')
        }),
        ('统计信息', {
            'fields': ('sales',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
