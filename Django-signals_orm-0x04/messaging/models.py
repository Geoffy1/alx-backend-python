# Django-signals_orm-0x04/messaging/models.py

from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # For Task 4
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies') # For Task 3
    edited = models.BooleanField(default=False) # For Task 1

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.content[:50]}..."

class MessageHistory(models.Model): # For Task 1
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"History for Message {self.message.id} at {self.edited_at.strftime('%Y-%m-%d %H:%M')}"