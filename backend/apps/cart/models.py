from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User
from apps.products.models import Product

class Cart(models.Model):
    """购物车"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.username}的购物车'

class CartItem(models.Model):
    """购物车商品"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name='购物车')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=1,
        verbose_name='数量'
    )
    selected = models.BooleanField(default=True, verbose_name='是否选中')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '购物车商品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['cart', 'product']  # 确保同一购物车中不会出现重复商品

    def __str__(self):
        return f'{self.cart.user.username}的购物车 - {self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        """保存前检查库存"""
        if self.quantity > self.product.stock:
            raise ValueError('商品库存不足')
        super().save(*args, **kwargs) 