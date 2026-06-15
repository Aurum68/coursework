"""
URL configuration for Print3d_Service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from models_3d.views import index, catalog, model_detail
from users.views import register, my_login, profile, edit_profile, my_logout, balance_replenishment
from order.views import add_to_cart, cart, update_cart, create_order, orders, order_detail, cancel_order

admin.site.site_header = 'Управление магазином 3D-печати'
admin.site.site_title = '3D Shop Admin'
admin.site.index_title = 'Добро пожаловать в панель управления'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('models/', catalog, name='models'),
    path('models/<int:id>/', model_detail, name='model_detail'),
    path('register/', register, name='register'),
    path('login/', my_login, name='login'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='profile_edit'),
    path('logout/', my_logout, name='logout'),
    path('balance/',balance_replenishment, name='balance_replenishment'),
    path('add/<int:model_id>/', add_to_cart, name='add_to_cart'),
    path('__debug__/', include('debug_toolbar.urls')),
    path('cart/', cart, name='cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('otders/create/', create_order, name='create_order'),
    path('orders/', orders, name='orders'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/cancel/<int:order_id>/', cancel_order, name='cancel_order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)