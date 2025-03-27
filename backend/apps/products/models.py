from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父分类')
    level = models.IntegerField(default=1, verbose_name='分类层级')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['level', 'id']

    def __str__(self):
        return self.name

class Product(models.Model):
    """商品"""
    name = models.CharField(max_length=200, verbose_name='商品名称')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='商品分类')
    description = models.TextField(verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    stock = models.IntegerField(default=0, verbose_name='库存数量')
    sales = models.IntegerField(default=0, verbose_name='销量')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """商品图片"""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='商品')
    image = models.ImageField(upload_to='products/', verbose_name='图片')
    is_main = models.BooleanField(default=False, verbose_name='是否主图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name
        ordering = ['-is_main']

    def __str__(self):
        return f'{self.product.name} - 图片'

class ProductSpecification(models.Model):
    """商品规格"""
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE, verbose_name='商品')
    name = models.CharField(max_length=100, verbose_name='规格名称')
    value = models.CharField(max_length=100, verbose_name='规格值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品规格'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return f'{self.product.name} - {self.name}: {self.value}'
