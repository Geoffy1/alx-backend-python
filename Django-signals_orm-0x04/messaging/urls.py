# Django-signals_orm-0x04/messaging/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('delete-account/', views.delete_user, name='delete_user'),
    path('conversations/', views.user_conversations, name='user_conversations'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
]