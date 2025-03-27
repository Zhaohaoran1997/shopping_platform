from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'coupons', views.CouponViewSet)
router.register(r'user-coupons', views.UserCouponViewSet, basename='user-coupon')

urlpatterns = [
    path('', include(router.urls)),
] 