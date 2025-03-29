from django.db import models
from django.conf import settings
from apps.orders.models import Order
from apps.products.models import Product

class ReturnRequest(models.Model):
    """退换货申请"""
    TYPE_CHOICES = (
        (1, '退货'),
        (2, '换货'),
    )
    
    STATUS_CHOICES = (
        (0, '待审核'),
        (1, '已同意'),
        (2, '已拒绝'),
        (3, '已完成'),
        (4, '已取消'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='returns', verbose_name='用户')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='商品', null=True, blank=True)
    quantity = models.IntegerField(verbose_name='退货数量', default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='退货总价', default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='优惠金额', default=0)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='实际金额', default=0)
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name='类型')
    reason = models.TextField(verbose_name='原因')
    description = models.TextField(verbose_name='问题描述', blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='状态')
    exchange_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exchange_returns',
        verbose_name='换货订单'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '退换货申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['order', 'product']  # 防止同一订单的同一商品重复申请

    def __str__(self):
        product_name = self.product.name if self.product else '整单'
        return f'{self.get_type_display()}申请 - {self.order.order_no} - {product_name}'

class ReturnImage(models.Model):
    """退换货图片"""
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name='images', verbose_name='退换货申请')
    image = models.ImageField(upload_to='returns/%Y/%m/%d/', verbose_name='图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '退换货图片'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.return_request.order.order_no} - 图片'
