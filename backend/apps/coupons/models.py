from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

class Coupon(models.Model):
    """消费券"""
    TYPE_CHOICES = (
        (1, '满减券'),
        (2, '折扣券'),
    )

    STATUS_CHOICES = (
        (0, '未开始'),
        (1, '进行中'),
        (2, '已结束'),
    )

    name = models.CharField(max_length=100, verbose_name='消费券名称')
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name='消费券类型')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='优惠金额/折扣率'
    )
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='最低使用金额'
    )
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'coupons'
        verbose_name = '消费券'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.type == 2 and (self.amount <= 0 or self.amount >= 10):
            raise ValueError('折扣券折扣率必须在0-10之间')
        super().save(*args, **kwargs)

class UserCoupon(models.Model):
    """用户消费券"""
    STATUS_CHOICES = (
        (0, '未使用'),
        (1, '已使用'),
        (2, '已过期'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name='消费券')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='使用状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='领取时间')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')

    class Meta:
        db_table = 'user_coupons'
        verbose_name = '用户消费券'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['user', 'coupon']  # 确保用户不会重复领取同一张消费券

    def __str__(self):
        return f'{self.user.username} - {self.coupon.name}'

    def use(self):
        """使用消费券"""
        if self.status != 0:
            raise ValueError('消费券状态不正确')
        self.status = 1
        self.used_at = timezone.now()
        self.save()
