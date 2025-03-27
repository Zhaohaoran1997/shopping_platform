from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.users.models import UserAddress

class Order(models.Model):
    STATUS_CHOICES = (
        (0, '待付款'),
        (1, '待发货'),
        (2, '待收货'),
        (3, '已完成'),
        (4, '已取消'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('alipay', '支付宝'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单编号')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总金额')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='订单状态')
    shipping_address = models.ForeignKey(UserAddress, on_delete=models.PROTECT, verbose_name='收货地址')
    shipping_name = models.CharField(max_length=50, verbose_name='收货人姓名')
    shipping_phone = models.CharField(max_length=20, verbose_name='收货人电话')
    shipping_province = models.CharField(max_length=50, verbose_name='省份')
    shipping_city = models.CharField(max_length=50, verbose_name='城市')
    shipping_district = models.CharField(max_length=50, verbose_name='区县')
    shipping_address_detail = models.TextField(verbose_name='详细地址')
    shipping_no = models.CharField(max_length=50, blank=True, null=True, verbose_name='物流单号')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='alipay', verbose_name='支付方式')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.get_status_display()}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='商品')
    product_name = models.CharField(max_length=100, verbose_name='商品名称')
    product_image = models.CharField(max_length=255, verbose_name='商品图片')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品单价')
    quantity = models.IntegerField(verbose_name='购买数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'order_items'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.order.order_no} - {self.product_name}'

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs) 