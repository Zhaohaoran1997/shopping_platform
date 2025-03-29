from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReturnRequestViewSet,
    OrderListViewSet,
    ReturnRequestDetailViewSet,
    ReturnRequestImageUploadView
)

router = DefaultRouter()
router.register('requests', ReturnRequestViewSet, basename='return-request')
router.register('orders', OrderListViewSet, basename='return-order')

urlpatterns = [
    path('', include(router.urls)),
    path('requests/<int:pk>/', ReturnRequestDetailViewSet.as_view({'get': 'retrieve'}), name='return-request-detail'),
    path('requests/<int:pk>/shipping/', ReturnRequestDetailViewSet.as_view({'post': 'update_shipping'}), name='return-request-shipping'),
    path('requests/upload/', ReturnRequestImageUploadView.as_view({'post': 'create'}), name='return-request-upload'),
] 