from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """购物车管理"""
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

class CartItemInline(admin.TabularInline):
    """购物车商品内联"""
    model = CartItem
    extra = 1
    fields = ['product', 'quantity', 'selected']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """购物车商品管理"""
    list_display = ['cart', 'product', 'quantity', 'selected', 'created_at']
    list_filter = ['selected', 'created_at']
    search_fields = ['cart__user__username', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at'] 