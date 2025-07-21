# messaging_app/chats/permissions.py
from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to access its messages and details (object-level permission).
    """
    message = "You are not a participant of this conversation."

    def has_permission(self, request, view):
        # View-level check: only authenticated users can access these views.
        # This is also handled by 'IsAuthenticated' in settings or viewsets.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Object-level check: only participants can interact with the conversation/message object.

        # If the object is a Conversation instance
        if isinstance(obj, type(view.queryset.model)): # Check if obj is of the same model type as view's queryset
            if hasattr(obj, 'participants'):
                return request.user in obj.participants.all()
        # If the object is a Message instance
        elif hasattr(obj, 'conversation') and hasattr(obj.conversation, 'participants'):
            return request.user in obj.conversation.participants.all()

        return False # Deny access if not a participant or object type is unexpected