"""
URL configuration for Agentswenda app.
"""
from django.urls import path
from . import views

app_name = 'Agentswenda'

urlpatterns = [
    path('api/analyze/', views.analyze_stock, name='analyze_stock'),
    path('api/history/', views.get_chat_history, name='get_chat_history'),
]
