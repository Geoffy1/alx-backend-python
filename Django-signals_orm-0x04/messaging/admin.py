# Django-signals_orm-0x04/messaging/admin.py

from django.contrib import admin
from .models import Message, Notification, MessageHistory

admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(MessageHistory)