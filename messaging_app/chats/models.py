import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Custom User Model
class CustomUser(AbstractUser):
    # Override the default 'id' with a UUIDField
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Override AbstractUser's first_name, last_name, and email to be NOT NULL/UNIQUE as per spec
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(unique=True, null=False, blank=False)

    # Additional fields as per specification
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest', null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # If you want to use email for authentication instead of username, uncomment these lines:
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['first_name', 'last_name', 'role'] # Customize required fields here

    class Meta:
        # Django automatically indexes primary keys. Add index for email as specified.
        indexes = [
            models.Index(fields=['email']),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email or f"User {self.id}"

# Conversation Model
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Using ManyToManyField for participants as a conversation involves multiple users
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return f"Conversation {self.conversation_id}"

# Message Model
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['sent_at'] # Order messages by time
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender.email} in {self.conversation.conversation_id} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
