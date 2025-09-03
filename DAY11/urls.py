"""
URL configuration for DAY11 project.

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

urlpatterns = [
    path('Agentswenda/', include('Agentswenda.urls')),
    path('admin/', admin.site.urls),
    # 缓存管理模块 - 匹配前端调用路径
    path('cache_management/api/', include('cache_management.urls')),
    # 用户行为记录模块 - 匹配前端调用路径
    path('user_behavior/api/', include('user_behavior.urls')),
    # 推荐系统模块 - 匹配前端调用路径
    path('recommendation/api/', include('recommendation.urls')),
    # RAG检索增强生成模块 - 匹配前端调用路径  
    path('rag/api/', include('rag.urls')),
    # 系统监控模块 - 新增系统API
    path('system/api/', include('system.urls')),
    # 产品管理模块
    path('api/products/', include('products.urls')),
    # 知识库模块
    path('api/knowledge/', include('knowledge.urls')),
]
