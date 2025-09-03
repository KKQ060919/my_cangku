"""
用户行为记录模块URL配置
"""
from django.urls import path
from . import views

app_name = 'user_behavior'

urlpatterns = [
    # 记录用户行为
    path('record/', views.RecordBehaviorAPIView.as_view(), name='record-behavior'),
    path('view/', views.RecordBehaviorAPIView.as_view(), name='record-view'),  # 前端使用的视图记录接口
    
    # 用户行为记录列表 - 新增前端需要的records端点
    path('records/', views.BehaviorRecordsAPIView.as_view(), name='behavior-records'),
    
    # 用户浏览历史
    path('history/<str:user_id>/', views.UserHistoryAPIView.as_view(), name='user-history'),
    
    # 用户偏好分析
    path('preferences/<str:user_id>/', views.UserPreferencesAPIView.as_view(), name='user-preferences'),
    
    # 热门商品统计
    path('popular/', views.PopularProductsAPIView.as_view(), name='popular-products'),
    
    # 用户行为统计
    path('stats/', views.BehaviorStatsAPIView.as_view(), name='behavior-stats'),
    
    # 行为趋势数据
    path('trends/', views.BehaviorTrendAPIView.as_view(), name='behavior-trends'),
]