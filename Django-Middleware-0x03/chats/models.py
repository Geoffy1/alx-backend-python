# messaging_app/chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone

# Custom User Manager to handle username creation if not provided
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        # Generate a unique username if not provided
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = str(uuid.uuid4()) # Use a UUID for guaranteed uniqueness

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # Unique identifier for external use

    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(unique=True, null=False, blank=False)

    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest', null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # Define email as the USERNAME_FIELD for authentication
    USERNAME_FIELD = 'email'
    # Required fields when creating a user via createsuperuser or CustomUserManager
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    # Fix for AbstractUser related_name clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        related_name='custom_user_groups_set', # Unique related_name
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_permissions_set', # Unique related_name
        related_query_name='custom_user',
    )

    # Assign your custom manager
    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"
        # Essential for Django to recognize this as the user model
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email or f"User {self.id}"

# Conversation Model
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Participants are CustomUsers
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return self.title or f"Conversation {self.conversation_id}"

# Message Model
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['sent_at'] # Default ordering for messages
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender.email} in {self.conversation.conversation_id} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"