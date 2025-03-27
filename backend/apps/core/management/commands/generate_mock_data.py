from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.products.models import Category, Product, ProductImage, ProductSpecification
from apps.orders.models import Order, OrderItem
from apps.coupons.models import Coupon, UserCoupon
from apps.users.models import UserAddress
from apps.cart.models import Cart, CartItem
from apps.returns.models import ReturnRequest, ReturnImage
import random
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = '生成测试数据，包括用户、商品、订单和优惠券'

    def handle(self, *args, **options):
        self.stdout.write('开始生成测试数据...')
        
        # 创建测试用户
        self.stdout.write('创建测试用户...')
        users = self.create_test_users()
        
        # 创建商品分类
        self.stdout.write('创建商品分类...')
        categories = self.create_categories()
        
        # 创建商品
        self.stdout.write('创建商品...')
        products = self.create_products(categories)
        
        # 创建用户地址
        self.stdout.write('创建用户地址...')
        addresses = self.create_user_addresses(users)
        
        # 创建优惠券
        self.stdout.write('创建优惠券...')
        coupons = self.create_coupons()
        
        # 创建用户优惠券
        self.stdout.write('创建用户优惠券...')
        self.create_user_coupons(users, coupons)
        
        # 创建订单
        self.stdout.write('创建订单...')
        orders = self.create_orders(users, products, addresses)
        
        # 创建购物车
        self.stdout.write('创建购物车...')
        self.create_carts(users, products)
        
        # 创建退换货申请
        self.stdout.write('创建退换货申请...')
        self.create_returns(users, orders)
        
        self.stdout.write(self.style.SUCCESS('测试数据生成完成！'))

    def create_test_users(self):
        """创建测试用户"""
        users = []
        for i in range(10):
            username = f'test_user_{i}'
            email = f'test_user_{i}@example.com'
            password = 'test123456'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'创建用户: {username}')
            
            users.append(user)
        return users

    def create_categories(self):
        """创建商品分类"""
        categories = []
        main_categories = ['电子产品', '服装', '食品', '家居', '图书']
        
        for main_name in main_categories:
            main_category, _ = Category.objects.get_or_create(
                name=main_name,
                defaults={'level': 1}
            )
            categories.append(main_category)
            
            # 创建子分类
            for i in range(3):
                sub_name = f'{main_name}子分类{i+1}'
                sub_category, _ = Category.objects.get_or_create(
                    name=sub_name,
                    parent=main_category,
                    defaults={'level': 2}
                )
                categories.append(sub_category)
        
        return categories

    def create_products(self, categories):
        """创建商品"""
        products = []
        product_names = [
            'iPhone 13', 'MacBook Pro', 'AirPods Pro',
            '休闲T恤', '牛仔裤', '运动鞋',
            '有机水果', '进口零食', '茶叶',
            '沙发', '床垫', '衣柜',
            '小说', '教材', '杂志'
        ]
        
        for name in product_names:
            category = random.choice(categories)
            price = random.randint(100, 10000)
            stock = random.randint(10, 100)
            
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': f'这是{name}的详细描述...',
                    'price': price,
                    'stock': stock,
                    'status': 'published',
                    'is_active': True
                }
            )
            
            if created:
                # 创建商品图片
                ProductImage.objects.create(
                    product=product,
                    image_url=f'https://example.com/images/{name}.jpg',
                    is_main=True
                )
                
                # 创建商品规格
                specs = [
                    ('颜色', '黑色'),
                    ('尺寸', '标准'),
                    ('材质', '优质')
                ]
                for spec_name, spec_value in specs:
                    ProductSpecification.objects.create(
                        product=product,
                        name=spec_name,
                        value=spec_value
                    )
                
                self.stdout.write(f'创建商品: {name}')
            
            products.append(product)
        
        return products

    def create_user_addresses(self, users):
        """创建用户地址"""
        addresses = []
        provinces = ['北京', '上海', '广东', '浙江', '江苏']
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京']
        
        for user in users:
            for i in range(2):  # 每个用户创建2个地址
                province = random.choice(provinces)
                city = random.choice(cities)
                district = f'{city}区'
                address = f'测试街道{i+1}号'
                
                address_obj, created = UserAddress.objects.get_or_create(
                    user=user,
                    defaults={
                        'receiver': f'收货人{i+1}',
                        'phone': f'1380000{random.randint(1000, 9999)}',
                        'province': province,
                        'city': city,
                        'district': district,
                        'address': address,
                        'is_default': i == 0
                    }
                )
                
                if created:
                    self.stdout.write(f'创建地址: {user.username} - {address}')
                
                addresses.append(address_obj)
        
        return addresses

    def create_coupons(self):
        """创建优惠券"""
        coupons = []
        now = timezone.now()
        
        # 满减券
        coupon_types = [
            ('满100减10', 1, 10, 100),
            ('满200减30', 1, 30, 200),
            ('满500减100', 1, 100, 500),
            ('9折优惠券', 2, 9, 100),
            ('8折优惠券', 2, 8, 200),
        ]
        
        for name, type_, amount, min_amount in coupon_types:
            coupon, created = Coupon.objects.get_or_create(
                name=name,
                defaults={
                    'type': type_,
                    'amount': amount,
                    'min_amount': min_amount,
                    'start_time': now,
                    'end_time': now + timedelta(days=30),
                    'status': 1
                }
            )
            
            if created:
                self.stdout.write(f'创建优惠券: {name}')
            
            coupons.append(coupon)
        
        return coupons

    def create_user_coupons(self, users, coupons):
        """创建用户优惠券"""
        for user in users:
            # 每个用户随机获得1-3张优惠券
            num_coupons = random.randint(1, 3)
            selected_coupons = random.sample(coupons, min(num_coupons, len(coupons)))
            
            for coupon in selected_coupons:
                # 随机设置优惠券状态
                status = random.choice([0, 1, 2])  # 0: 未使用, 1: 已使用, 2: 已过期
                used_at = None
                if status == 1:  # 如果状态是已使用，设置使用时间
                    used_at = timezone.now() - timedelta(days=random.randint(1, 30))
                
                UserCoupon.objects.get_or_create(
                    user=user,
                    coupon=coupon,
                    defaults={
                        'status': status,
                        'used_at': used_at
                    }
                )

    def create_orders(self, users, products, addresses):
        """创建订单"""
        order_statuses = [0, 1, 2, 3, 4]  # 待付款、待发货、待收货、已完成、已取消
        orders = []
        
        for user in users:
            # 每个用户创建1-3个订单
            num_orders = random.randint(1, 3)
            user_addresses = [addr for addr in addresses if addr.user == user]
            
            for _ in range(num_orders):
                status = random.choice(order_statuses)
                address = random.choice(user_addresses)
                
                # 创建订单
                order = Order.objects.create(
                    user=user,
                    order_no=f'ORDER{random.randint(100000, 999999)}',
                    total_amount=Decimal('0'),
                    status=status,
                    shipping_address=address,
                    shipping_name=address.receiver,
                    shipping_phone=address.phone,
                    shipping_province=address.province,
                    shipping_city=address.city,
                    shipping_district=address.district,
                    shipping_address_detail=address.address,
                    payment_method='alipay'
                )
                
                # 添加订单商品
                num_items = random.randint(1, 3)
                selected_products = random.sample(products, min(num_items, len(products)))
                
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    price = product.price
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_image=product.images.first().image_url if product.images.exists() else '',
                        price=price,
                        quantity=quantity,
                        total_price=price * quantity
                    )
                
                # 更新订单总金额
                order.total_amount = sum(item.total_price for item in order.items.all())
                order.save()
                
                self.stdout.write(f'创建订单: {order.order_no}')
                orders.append(order)
        
        return orders

    def create_carts(self, users, products):
        """创建购物车数据"""
        for user in users:
            # 创建购物车
            cart, created = Cart.objects.get_or_create(user=user)
            
            if created:
                self.stdout.write(f'创建购物车: {user.username}')
            
            # 添加购物车商品
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                selected = random.choice([True, False])
                
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={
                        'quantity': quantity,
                        'selected': selected
                    }
                )

    def create_returns(self, users, orders):
        """创建退换货申请"""
        return_types = [1, 2]  # 1: 退货, 2: 换货
        return_statuses = [0, 1, 2, 3, 4]  # 待审核、已同意、已拒绝、已完成、已取消
        
        for user in users:
            # 获取用户的已完成订单
            user_orders = [order for order in orders if order.user == user and order.status == 3]
            
            if not user_orders:
                continue
            
            # 每个用户随机对1-2个已完成订单申请退换货
            num_returns = random.randint(1, 2)
            selected_orders = random.sample(user_orders, min(num_returns, len(user_orders)))
            
            for order in selected_orders:
                return_type = random.choice(return_types)
                status = random.choice(return_statuses)
                reason = f'测试退换货原因 - {random.choice(["商品质量问题", "商品与描述不符", "商品损坏", "其他原因"])}'
                
                return_request, created = ReturnRequest.objects.get_or_create(
                    order=order,
                    defaults={
                        'user': user,
                        'type': return_type,
                        'reason': reason,
                        'status': status
                    }
                )
                
                if created:
                    self.stdout.write(f'创建退换货申请: {order.order_no} - {return_request.get_type_display()}')
                    
                    # 创建退换货图片（示例URL）
                    ReturnImage.objects.create(
                        return_request=return_request,
                        image='returns/example.jpg'  # 实际使用时需要替换为真实图片
                    )