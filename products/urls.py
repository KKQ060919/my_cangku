"""
产品管理应用URL配置
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 商品列表API
    path('list/', views.product_list, name='product_list'),
    
    # 商品详情API
    path('detail/<str:product_id>/', views.product_detail, name='product_detail'),
    
    # 获取商品类别API
    path('categories/', views.get_categories, name='get_categories'),
    
    # 获取品牌列表API
    path('brands/', views.get_brands, name='get_brands'),
]
