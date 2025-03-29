from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserAddressViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

# 将地址相关的 URL 放在用户 URL 下
user_address_router = DefaultRouter()
user_address_router.register(r'addresses', UserAddressViewSet, basename='user-address')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:user_id>/', include(user_address_router.urls)),
] 