from django.db import models
from django.conf import settings
from apps.orders.models import Order

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

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns', verbose_name='订单')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='returns', verbose_name='用户')
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name='类型')
    reason = models.TextField(verbose_name='原因')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '退换货申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()}申请 - {self.order.order_no}'

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
