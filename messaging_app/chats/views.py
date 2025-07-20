# messaging_app/chats/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import CustomUser, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at') # Order by most recent
    serializer_class = ConversationSerializer
    # We can explicitly set permission classes here if needed,
    # but DEFAULT_PERMISSION_CLASSES in settings.py will apply.
    # permission_classes = [IsAuthenticated] # Assuming IsAuthenticated is default globally

    def perform_create(self, serializer):
        # When creating a new conversation, the creator should automatically be a participant.
        # The API request might send 'participants' IDs, or we assume it's just the creator
        # initially and others are added later.
        # For simplicity, let's assume 'participants' are provided in the request data,
        # but the current user is always included.

        # Get the authenticated user
        user = self.request.user

        # If 'participants' are sent in the request, make sure the current user is among them.
        # If not sent, just make the current user the sole participant initially.
        participant_ids = self.request.data.get('participants', [])
        if isinstance(participant_ids, list):
            # Ensure current user's ID is in the list (UUID form)
            if str(user.id) not in [str(p_id) for p_id in participant_ids]:
                participant_ids.append(str(user.id))
        else: # If participants is not a list (e.g., single ID or not provided)
            participant_ids = [str(user.id)] # Just the current user

        # Validate that all participant_ids actually refer to existing CustomUser objects
        # And retrieve the actual CustomUser instances
        participants = []
        for p_id in participant_ids:
            try:
                # Filter by id (UUIDField)
                p_user = CustomUser.objects.get(id=p_id)
                participants.append(p_user)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(f"Participant with ID {p_id} does not exist.")


        # Save the conversation instance, but don't commit to DB yet to add m2m field
        instance = serializer.save()
        # Now add the participants
        instance.participants.set(participants) # Set expects a list of model instances

        # Note: The `perform_create` method typically handles the instance saving.
        # Our ConversationSerializer has `participants` as read_only=True,
        # so we manually handle it here. If we wanted to allow adding participants
        # during creation via the serializer, we'd adjust the serializer.

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Adds a participant to an existing conversation.
        Requires 'user_id' in the request data.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_add = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user_to_add in conversation.participants.all():
            return Response({"detail": "User is already a participant."}, status=status.HTTP_200_OK)

        conversation.participants.add(user_to_add)
        conversation.save() # Save the M2M change
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    # The queryset will be dynamically filtered based on conversation if needed,
    # or show all messages if globally accessible.
    # For this task, let's keep it simple and allow filtering later if needed.
    queryset = Message.objects.all().order_by('sent_at')

    def perform_create(self, serializer):
        # When creating a message, sender is the current authenticated user.
        # Conversation ID must be provided in the request.
        # The MessageSerializer's `conversation` field will handle the FK link.

        conversation_id = self.request.data.get('conversation') # Get conversation ID from request body
        if not conversation_id:
            raise serializers.ValidationError({"conversation": "Conversation ID is required."})

        try:
            # Ensure the conversation exists and the sender is a participant
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if self.request.user not in conversation.participants.all():
                raise serializers.ValidationError("You are not a participant of this conversation.")

        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"conversation": "Conversation not found."})

        serializer.save(sender=self.request.user, conversation=conversation)

    # Optional: Custom action to get messages for a specific conversation
    @action(detail=True, methods=['get'])
    def messages_in_conversation(self, request, pk=None):
        """
        Retrieves all messages for a specific conversation ID.
        pk here refers to message_id, but if we want to filter by conversation,
        we'd need a different route or filter the main queryset.
        This action is better placed in ConversationViewSet.
        """
        return Response({"detail": "This action is typically placed in ConversationViewSet or use filters on this viewset."})

""" **Explanation:**

* **`ConversationViewSet`**:
    * Inherits `ModelViewSet` for CRUD.
    * `queryset` retrieves all conversations, ordered by creation time.
    * `serializer_class` links it to your `ConversationSerializer`.
    * **`perform_create(self, serializer)`**: This method is overridden to handle the many-to-many `participants` relationship. When a new conversation is created:
        * It gets the `participants` IDs from the request data.
        * **Crucially, it ensures the current authenticated user (`self.request.user`) is always added as a participant.**
        * It retrieves `CustomUser` instances for all provided and added participant IDs.
        * It saves the conversation instance and then uses `instance.participants.set()` to assign the users. This ensures the many-to-many relationship is correctly established.
    * **`add_participant` action**: This demonstrates how to add a custom endpoint. It allows adding a user to an existing conversation, useful for group chats.

* **`MessageViewSet`**:
    * Inherits `ModelViewSet` for CRUD.
    * `queryset` retrieves all messages, ordered by `sent_at`.
    * `serializer_class` links it to your `MessageSerializer`.
    * **`perform_create(self, serializer)`**: This is overridden to automatically set the `sender` of the message to the current authenticated user (`self.request.user`) and to link the message to the correct `conversation` based on an `id` provided in the request body. It also adds a check to ensure the sender is actually a participant of the target conversation.

 """