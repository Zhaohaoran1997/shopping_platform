from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    """购物车视图集"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取用户的购物车"""
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        """获取或创建用户的购物车"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """添加商品到购物车"""
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # 检查是否已存在该商品
                cart_item = CartItem.objects.filter(
                    cart=cart,
                    product_id=serializer.validated_data['product_id']
                ).first()
                
                if cart_item:
                    # 如果已存在，更新数量
                    cart_item.quantity += serializer.validated_data.get('quantity', 1)
                    cart_item.save()
                else:
                    # 如果不存在，创建新项
                    serializer.save(cart=cart)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def update_item(self, request, pk=None):
        """更新购物车商品数量"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or not quantity:
            return Response(
                {'error': '缺少必要参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            cart_item.quantity = quantity
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {'error': '购物车商品不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """删除购物车商品"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'error': '缺少商品ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {'error': '购物车商品不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'])
    def clear(self, request, pk=None):
        """清空购物车"""
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'])
    def select_item(self, request, pk=None):
        """选择/取消选择购物车商品"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        selected = request.data.get('selected', True)
        
        if not item_id:
            return Response(
                {'error': '缺少商品ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            cart_item.selected = selected
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {'error': '购物车商品不存在'},
                status=status.HTTP_404_NOT_FOUND
            ) 