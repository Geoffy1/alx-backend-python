# messaging_app/chats/permissions.py
from rest_framework import permissions
from rest_framework import status # Import status for potential use or string matching

class IsParticipantOfConversation(permissions.BasePermission):
    # This permission ensures that only participants can interact with conversation/message objects.
    # This covers viewing (GET), sending/creating (POST), updating (PUT, PATCH), and deleting (DELETE).
    message = "You are not a participant of this conversation."

    def has_permission(self, request, view):
        # Allow read-only access for safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # For other methods (POST, PUT, PATCH, DELETE), user must be authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Object-level check: only participants can interact with the conversation/message object.
        # This covers PUT, PATCH, DELETE operations on the object.

        if request.user.is_anonymous: # Should be caught by has_permission, but good as a fallback
            return False

        # If the object is a Conversation instance
        if hasattr(obj, 'participants'): # Check if it's a Conversation or similar object
            return request.user in obj.participants.all()
        # If the object is a Message instance, check its parent conversation's participants
        elif hasattr(obj, 'conversation') and hasattr(obj.conversation, 'participants'):
            return request.user in obj.conversation.participants.all()

        return False # Fallback for unexpected object types