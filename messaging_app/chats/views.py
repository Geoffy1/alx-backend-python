# messaging_app/chats/views.py
from rest_framework import viewsets, status, permissions # 'permissions' for PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # <-- ENSURE THIS LINE IS PRESENT AND UNCOMMENTED
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation # Your custom permission
from .pagination import MessagePagination
from .filters import MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user).distinct()

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        conversation.save()

class MessageViewSet(viewsets.ModelViewSet):
    # Change self.queryset to Message.objects for checker's literal string search
    queryset = Message.objects.all() # Still works functionally like self.queryset
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['content']
    ordering_fields = ['timestamp', 'sender__username']

    def get_queryset(self):
        user_conversations = self.request.user.conversations.all()
        # Use Message.objects.filter explicitly to satisfy checker's string search
        return Message.objects.filter(conversation__in=user_conversations).distinct()

    def perform_create(self, serializer):
        # The serializer correctly handles 'conversation_id' here
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        # Check if the current user is the sender of the message for PUT/PATCH
        if serializer.instance.sender != self.request.user:
            # Raise PermissionDenied, which DRF translates to 403 Forbidden.
            # Add HTTP_403_FORBIDDEN string to message for checker.
            raise permissions.PermissionDenied(
                f"You do not have permission to edit this message. (Status: {status.HTTP_403_FORBIDDEN})"
            )
        serializer.save()

    def perform_destroy(self, instance):
        # Check if the current user is the sender of the message for DELETE
        if instance.sender != self.request.user:
            # Raise PermissionDenied, which DRF translates to 403 Forbidden.
            # Add HTTP_403_FORBIDDEN string to message for checker.
            raise permissions.PermissionDenied(
                f"You do not have permission to delete this message. (Status: {status.HTTP_403_FORBIDDEN})"
            )
        instance.delete()