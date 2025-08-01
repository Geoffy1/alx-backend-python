# Django-signals_orm-0x04/chats/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('delete-account/', views.delete_user_account, name='delete_user_account'),
    path('', views.home, name='home'), # A simple home page for redirection,
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
]