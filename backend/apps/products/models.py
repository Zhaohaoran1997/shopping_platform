from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """商品分类"""
    name = models.CharField(_('分类名称'), max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('父分类'))
    level = models.IntegerField(_('分类层级'), default=1)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('商品分类')
        verbose_name_plural = _('商品分类')
        ordering = ['level', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        super().save(*args, **kwargs)

class Product(models.Model):
    """商品"""
    STATUS_CHOICES = [
        ('draft', _('草稿')),
        ('published', _('已发布')),
        ('archived', _('已归档')),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('商品分类'))
    name = models.CharField(_('商品名称'), max_length=200)
    description = models.TextField(_('商品描述'))
    price = models.DecimalField(_('商品价格'), max_digits=10, decimal_places=2)
    stock = models.IntegerField(_('库存数量'), default=0)
    sales = models.IntegerField(_('销量'), default=0)
    status = models.CharField(_('商品状态'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(_('是否上架'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('商品')
        verbose_name_plural = _('商品')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """商品图片"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('商品'))
    image_url = models.URLField(_('图片链接'), null=True, blank=True)
    is_main = models.BooleanField(_('是否主图'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('商品图片')
        verbose_name_plural = _('商品图片')
        ordering = ['-is_main', 'created_at']

    def __str__(self):
        return f"{self.product.name}的图片"

class ProductSpecification(models.Model):
    """商品规格"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications', verbose_name=_('商品'))
    name = models.CharField(_('规格名称'), max_length=100)
    value = models.CharField(_('规格值'), max_length=200)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('商品规格')
        verbose_name_plural = _('商品规格')
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
