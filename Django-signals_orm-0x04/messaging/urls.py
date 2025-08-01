# Django-signals_orm-0x04/messaging/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_user'),
    path('', views.home, name='home'),
]