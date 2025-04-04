"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),  # 用户相关API
    path('products/', include('apps.products.urls')),  # 商品相关API
    path('cart/', include('apps.cart.urls')),  # 购物车相关API
    path('orders/', include('apps.orders.urls')),  # 订单相关API
    path('coupons/', include('apps.coupons.urls')),  # 消费券相关API
    path('returns/', include('apps.returns.urls')),  # 退换货相关API
]

# 开发环境下添加媒体文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
