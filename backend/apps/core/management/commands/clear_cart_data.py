from django.core.management.base import BaseCommand
from apps.cart.models import Cart, CartItem

class Command(BaseCommand):
    help = '清空购物车和购物车商品数据'

    def handle(self, *args, **options):
        self.stdout.write('开始清空购物车数据...')
        
        # 清空购物车商品表
        CartItem.objects.all().delete()
        self.stdout.write('已清空购物车商品表')
        
        # 清空购物车表
        Cart.objects.all().delete()
        self.stdout.write('已清空购物车表')
        
        self.stdout.write(self.style.SUCCESS('购物车数据清空完成！')) 