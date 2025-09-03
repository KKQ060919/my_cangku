"""
推荐系统模块URL配置
"""
from django.urls import path
from . import views

app_name = 'recommendation'

urlpatterns = [
    # 商品推荐
    path('products/', views.RecommendationsAPIView.as_view(), name='recommendations'),
    path('recommend/', views.RecommendationsAPIView.as_view(), name='recommend'),  # 前端使用的推荐接口
    
    # 问答+推荐
    path('qa/', views.QAWithRecommendationAPIView.as_view(), name='qa-recommendation'),
    
    # 推荐点击统计
    path('click/', views.RecommendationClickAPIView.as_view(), name='click-tracking'),
    
    # 用户反馈
    path('feedback/', views.RecommendationFeedbackAPIView.as_view(), name='recommendation-feedback'),
    
    # 对话历史
    path('conversations/<str:user_id>/', views.ConversationHistoryAPIView.as_view(), name='conversation-history'),
    
    # 推荐统计
    path('stats/', views.RecommendationStatsAPIView.as_view(), name='recommendation-stats'),
]