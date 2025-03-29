from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
import time
import random

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取用户的订单列表"""
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """创建订单"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取要购买的商品信息列表，每个商品包含id和quantity
        order_items = request.data.get('items', [])
        if not order_items:
            return Response(
                {'detail': '订单商品不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 从购物车中获取商品信息
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.filter(product_id__in=[item['id'] for item in order_items])
            
            if not cart_items:
                return Response(
                    {'detail': '购物车中没有选中的商品'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Cart.DoesNotExist:
            return Response(
                {'detail': '购物车为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证购物车中的商品数量是否与订单一致
        for item in order_items:
            try:
                cart_item = cart_items.get(product_id=item['id'])
                if cart_item.quantity != item['quantity']:
                    return Response(
                        {'detail': f'商品 {cart_item.product.name} 数量不匹配'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except CartItem.DoesNotExist:
                return Response(
                    {'detail': f'商品ID {item["id"]} 不在购物车中'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 计算订单金额
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        shipping_fee = 10  # 固定运费
        discount_amount = 0

        # 计算优惠券折扣
        if serializer.validated_data.get('coupon'):
            coupon = serializer.validated_data['coupon']
            if total_amount >= coupon.min_amount:
                if coupon.type == 1:  # 满减券
                    discount_amount = coupon.amount
                elif coupon.type == 2:  # 折扣券
                    discount_amount = total_amount * (1 - coupon.amount / 10)

        final_amount = total_amount + shipping_fee - discount_amount

        # 创建订单
        with transaction.atomic():
            # 创建订单
            order = Order.objects.create(
                user=request.user,
                order_no=f'ORDER{int(time.time())}{random.randint(1000, 9999)}',
                total_amount=total_amount,
                shipping_fee=shipping_fee,
                discount_amount=discount_amount,
                final_amount=final_amount,
                payment_method=serializer.validated_data.get('payment_method', 'alipay'),
                remark=serializer.validated_data.get('remark', ''),
                shipping_name=serializer.validated_data['shipping_name'],
                shipping_phone=serializer.validated_data['shipping_phone'],
                shipping_province=serializer.validated_data['shipping_province'],
                shipping_city=serializer.validated_data['shipping_city'],
                shipping_district=serializer.validated_data['shipping_district'],
                shipping_address_detail=serializer.validated_data['shipping_address_detail'],
                shipping_address_id=serializer.validated_data['address_id'],
                coupon=serializer.validated_data.get('coupon'),
                user_coupon_id=serializer.validated_data.get('coupon_id')
            )

            # 创建订单项并更新库存
            for item in order_items:
                cart_item = cart_items.get(product_id=item['id'])
                product = cart_item.product
                if product.stock < item['quantity']:
                    raise ValueError(f'商品 {product.name} 库存不足')
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_image=product.images.first().image_url if product.images.exists() else '',
                    price=product.price,
                    quantity=item['quantity'],
                    total_price=product.price * item['quantity']
                )

                # 更新商品库存
                product.stock -= item['quantity']
                product.sales += item['quantity']
                product.save()

            # 从购物车中删除已购买的商品
            cart_items.delete()

            # 如果使用了优惠券，标记为已使用
            if serializer.validated_data.get('coupon'):
                user_coupon = UserCoupon.objects.get(
                    id=serializer.validated_data['coupon_id'],
                    user=request.user
                )
                user_coupon.use()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """支付订单"""
        order = self.get_object()
        if order.status != 0:  # 待付款
            return Response(
                {'detail': '订单状态不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 模拟支付过程
        payment_method = request.data.get('payment_method', 'alipay')
        if payment_method not in ['alipay', 'wechat']:
            return Response(
                {'detail': '不支持的支付方式'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 模拟支付延迟
        time.sleep(1)
        
        # 生成支付流水号
        payment_no = f'PAY{int(time.time())}{random.randint(1000, 9999)}'
        
        # 更新订单状态
        order.status = 1  # 待发货
        order.payment_no = payment_no
        order.payment_time = timezone.now()
        order.save()

        return Response({
            'detail': '支付成功',
            'payment_no': payment_no,
            'payment_time': order.payment_time,
            'payment_method': payment_method,
            'amount': order.final_amount
        })

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """发货"""
        order = self.get_object()
        if order.status != 1:  # 待发货
            return Response(
                {'detail': '订单状态不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shipping_no = request.data.get('shipping_no')
        if not shipping_no:
            return Response(
                {'detail': '请提供物流单号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.shipping_no = shipping_no
        order.status = 2  # 待收货
        order.save()
        return Response({'detail': '发货成功'})

    @action(detail=True, methods=['post'])
    def confirm_receive(self, request, pk=None):
        """确认收货"""
        order = self.get_object()
        if order.status != 2:  # 待收货
            return Response(
                {'detail': '订单状态不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 3  # 已完成
        order.save()
        return Response({'detail': '确认收货成功'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()
        if order.status != 0:  # 待付款
            return Response(
                {'detail': '订单状态不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 4  # 已取消
        order.save()
        return Response({'detail': '取消订单成功'})

    @action(detail=True, methods=['get'])
    def shipping_info(self, request, pk=None):
        """获取物流信息"""
        order = self.get_object()
        return Response({
            'shipping_no': order.shipping_no,
            'shipping_address': {
                'name': order.shipping_name,
                'phone': order.shipping_phone,
                'province': order.shipping_province,
                'city': order.shipping_city,
                'district': order.shipping_district,
                'address': order.shipping_address_detail
            }
        })

@admin.site.admin_view
def admin_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 0:  # 待付款
        order.status = 4  # 已取消
        order.save()
        messages.success(request, f'订单 {order.order_no} 已取消')
    else:
        messages.error(request, f'订单 {order.order_no} 状态不允许取消')
    return redirect(reverse('admin:orders_order_changelist'))

@admin.site.admin_view
def admin_ship_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 1:  # 待发货
        order.status = 2  # 待收货
        order.save()
        messages.success(request, f'订单 {order.order_no} 已发货')
    else:
        messages.error(request, f'订单 {order.order_no} 状态不允许发货')
    return redirect(reverse('admin:orders_order_changelist')) 