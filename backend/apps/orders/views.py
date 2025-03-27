from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.cart.models import CartItem
from apps.products.models import Product

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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """创建订单"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取购物车商品
        cart_items = CartItem.objects.filter(cart__user=request.user)
        if not cart_items.exists():
            return Response(
                {'detail': '购物车为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 计算总金额
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        # 创建订单
        order = Order.objects.create(
            user=request.user,
            order_no=f'ORDER{timezone.now().strftime("%Y%m%d%H%M%S")}{request.user.id}',
            total_amount=total_amount,
            **serializer.validated_data
        )

        # 创建订单商品并更新库存
        for cart_item in cart_items:
            product = cart_item.product
            if product.stock < cart_item.quantity:
                order.delete()
                return Response(
                    {'detail': f'商品 {product.name} 库存不足'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_image=product.images.first().image.url if product.images.exists() else '',
                price=product.price,
                quantity=cart_item.quantity,
                total_price=product.price * cart_item.quantity
            )

            # 更新商品库存
            product.stock -= cart_item.quantity
            product.sales += cart_item.quantity
            product.save()

        # 清空购物车
        cart_items.delete()

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
        
        # 这里应该调用支付宝支付接口
        # 为了演示，我们直接更新订单状态
        order.status = 1  # 待发货
        order.save()
        return Response({'detail': '支付成功'})

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