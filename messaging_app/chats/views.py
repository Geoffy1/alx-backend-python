# messaging_app/chats/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Already defined as default in settings
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation # Import your custom permission
from .pagination import MessagePagination # Will be created in Task 2
from .filters import MessageFilter # Will be created in Task 2


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    # Apply permissions: IsAuthenticated (from settings default) + custom object-level permission
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        """
        Ensure a user can only see conversations they are a participant of.
        This filters the list view and also limits the scope for object-level lookups.
        """
        return self.queryset.filter(participants=self.request.user).distinct()

    def perform_create(self, serializer):
        """
        When a conversation is created, automatically add the creating user as a participant.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save() # Save again to persist ManyToMany changes

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    # Apply permissions: IsAuthenticated (from settings default) + custom object-level permission
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination # Will be applied in Task 2
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter] # Will be applied in Task 2
    filterset_class = MessageFilter # Will be applied in Task 2
    search_fields = ['content'] # Example: allow searching message content by text
    ordering_fields = ['timestamp', 'sender__username'] # Example: allow ordering messages

    def get_queryset(self):
        """
        Ensure a user can only see messages from conversations they are a part of.
        """
        user_conversations = self.request.user.conversations.all()
        return self.queryset.filter(conversation__in=user_conversations).distinct()

    def perform_create(self, serializer):
        """
        When a message is created, automatically set the sender to the current authenticated user.
        """
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        """
        Only allow the message sender to update their own message.
        The IsParticipantOfConversation already ensures they are in the conversation.
        """
        if serializer.instance.sender != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this message.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Only allow the message sender to delete their own message.
        """
        if instance.sender != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to delete this message.")
        instance.delete()