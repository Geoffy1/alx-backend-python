# messaging_app/chats/permissions.py
from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view, update, or delete it.
    """
    message = "You are not a participant of this conversation."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any participant, so we'll always allow GET, HEAD, or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.participants.all()

        # Write permissions are only allowed to participants
        return request.user in obj.participants.all()

class IsSenderOfMessage(permissions.BasePermission):
    """
    Custom permission to only allow senders of a message to update or delete it.
    Allows participants to view messages (SAFE_METHODS).
    """
    message = "You are not the sender of this message or not a participant in the conversation."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any participant of the conversation
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()

        # Write permissions (PUT, PATCH, DELETE) are only allowed to the sender
        return obj.sender == request.user