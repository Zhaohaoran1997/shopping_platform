from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.users.models import User

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
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='商品评分'
    )
    review_count = models.IntegerField(default=0, verbose_name='评价数量')
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
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name
        ordering = ['is_main', 'order']

    def __str__(self):
        return f'{self.product.name} - 图片 {self.order}'

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

class ProductReview(models.Model):
    """商品评价"""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name='商品')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='评分'
    )
    content = models.TextField(verbose_name='评价内容')
    images = models.ImageField(upload_to='reviews/', null=True, blank=True, verbose_name='评价图片')
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品评价'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 对 {self.product.name} 的评价'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 更新商品的评分和评价数量
        product = self.product
        reviews = product.reviews.all()
        total_rating = sum(review.rating for review in reviews)
        product.rating = total_rating / reviews.count() if reviews.count() > 0 else 0
        product.review_count = reviews.count()
        product.save()
