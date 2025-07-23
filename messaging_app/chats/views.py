# messaging_app/chats/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend # For django-filters

from .models import CustomUser, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsSenderOfMessage
from .filters import MessageFilter # Your custom filter class

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    Only allows authenticated users to list/retrieve other users.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can view users
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name', 'created_at']

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be created, viewed, updated, or deleted.
    Access is restricted to participants only.
    """
    queryset = Conversation.objects.all().prefetch_related('participants')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Ensure users only see conversations they are a part of
        return self.queryset.filter(participants=self.request.user).distinct()

    def perform_create(self, serializer):
        # Pass the request context to the serializer for user access
        serializer.save(request=self.request)

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be created, viewed, updated, or deleted.
    View access is for conversation participants. Update/delete only by sender.
    """
    queryset = Message.objects.all().select_related('sender', 'conversation')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsSenderOfMessage] # Apply custom message permissions

    # Filtering and search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter # Apply your custom message filter
    search_fields = ['message_body']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        # Ensure users only see messages from conversations they are a part of
        user_conversations = self.request.user.conversations.all()
        return self.queryset.filter(conversation__in=user_conversations).distinct()

    def perform_create(self, serializer):
        # Pass the request context to the serializer for user access and conversation validation
        serializer.save(request=self.request)

    # No custom perform_update/destroy needed as default DRF handles it
    # and permissions take care of authorization.