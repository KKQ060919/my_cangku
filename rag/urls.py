"""
RAG模块URL配置
"""
from django.urls import path
from . import views

app_name = 'rag'

urlpatterns = [
    # RAG问答 - 原有端点
    path('question/', views.RAGQuestionAPIView.as_view(), name='rag-question'),
    
    # RAG问答 - 前端兼容端点
    path('ask/', views.RAGQuestionAPIView.as_view(), name='rag-ask'),
    
    # 用户反馈端点 - 新增
    path('feedback/', views.FeedbackAPIView.as_view(), name='rag-feedback'),
    
    # 构建向量数据库
    path('build/', views.BuildVectorStoreAPIView.as_view(), name='build-vector-store'),
    
    # 对话历史
    path('conversations/<str:user_id>/', views.ConversationHistoryAPIView.as_view(), name='conversation-history'),
    
    # RAG统计
    path('stats/', views.RAGStatsAPIView.as_view(), name='rag-stats'),
    
    # 热门问题 - 新增前端需要的popular_questions端点
    path('popular_questions/', views.PopularQuestionsAPIView.as_view(), name='popular-questions'),
    
    # 清空缓存
    path('clear/', views.ClearCacheAPIView.as_view(), name='clear-cache'),
]