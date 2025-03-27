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
        queryset = Order.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get cart items
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response(
                {'detail': '购物车为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total amount
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_no=f'ORDER{timezone.now().strftime("%Y%m%d%H%M%S")}{request.user.id}',
            total_amount=total_amount,
            **serializer.validated_data
        )

        # Create order items and update product stock
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

            # Update product stock
            product.stock -= cart_item.quantity
            product.sales += cart_item.quantity
            product.save()

        # Clear cart
        cart_items.delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.STATUS_CHOICES[0][0]:  # 待付款
            return Response(
                {'detail': '订单状态不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mock payment process
        order.status = Order.STATUS_CHOICES[1][0]  # 待发货
        order.payment_time = timezone.now()
        order.payment_method = request.data.get('payment_method', '支付宝')  # 支付方式
        order.payment_no = f'PAY{timezone.now().strftime("%Y%m%d%H%M%S")}{order.id}'  # 支付流水号
        order.save()

        return Response({
            'detail': '支付成功',
            'payment_no': order.payment_no,
            'payment_time': order.payment_time
        })

    @action(detail=True, methods=['post'])
    def confirm_receive(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.STATUS_CHOICES[2][0]:  # 待收货
            return Response(
                {'detail': '订单状态不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = Order.STATUS_CHOICES[3][0]  # 已完成
        order.complete_time = timezone.now()
        order.save()

        return Response({'detail': '确认收货成功'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.STATUS_CHOICES[0][0]:  # 待付款
            return Response(
                {'detail': '订单状态不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = Order.STATUS_CHOICES[4][0]  # 已取消
        order.save()

        return Response({'detail': '取消订单成功'})

    @action(detail=True, methods=['get'])
    def shipping_info(self, request, pk=None):
        order = self.get_object()
        return Response({
            'shipping_no': order.shipping_no,
            'shipping_company': order.shipping_company,
            'shipping_time': order.shipping_time,
            'shipping_address': {
                'name': order.shipping_name,
                'phone': order.shipping_phone,
                'province': order.shipping_province,
                'city': order.shipping_city,
                'district': order.shipping_district,
                'address': order.shipping_address_detail
            }
        }) 