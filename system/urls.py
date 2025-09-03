"""
系统监控模块URL配置
"""
from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    # 系统指标
    path('metrics/', views.SystemMetricsAPIView.as_view(), name='system-metrics'),
    
    # 数据库统计
    path('database_stats/', views.DatabaseStatsAPIView.as_view(), name='database-stats'),
    
    # 系统日志
    path('logs/', views.SystemLogsAPIView.as_view(), name='system-logs'),
]
