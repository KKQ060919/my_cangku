"""
知识库管理应用URL配置
"""
from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    # 知识库相关API将来可以在这里添加
    # path('', views.KnowledgeListView.as_view(), name='list'),
    # path('<int:knowledge_id>/', views.KnowledgeDetailView.as_view(), name='detail'),
]
