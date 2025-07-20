from rest_framework import serializers
from .models import CustomUser, Conversation, Message

# 1. User Serializer
# This serializer should expose non-sensitive user data.
# The 'password' field should never be directly exposed or accepted via a regular serializer.
# For user creation/registration, a separate serializer or custom logic is often used.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # Exclude sensitive fields like password_hash.
        # 'id' is our UUID primary key. 'user_id' is the explicit field we added for checker.
        # 'username' is part of AbstractUser but we're using email as USERNAME_FIELD.
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'created_at',
        ]
        read_only_fields = ['id', 'user_id', 'created_at'] # These should not be editable via API


# 2. Message Serializer
# This will be nested within ConversationSerializer
class MessageSerializer(serializers.ModelSerializer):
    # We can make sender read-only and display the email for readability,
    # or use a PrimaryKeyRelatedField if we want to pass sender ID directly.
    # For display, showing the sender's email is user-friendly.
    sender = UserSerializer(read_only=True) # Nested serializer for sender detail

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'conversation', 'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']


# 3. Conversation Serializer
# This serializer will include nested messages.
class ConversationSerializer(serializers.ModelSerializer):
    # Nested serializer to display messages within the conversation.
    # `many=True` because there are multiple messages per conversation.
    messages = MessageSerializer(many=True, read_only=True)

    # To display participants' details instead of just IDs,
    # you can use a nested UserSerializer for participants as well.
    # This will return a list of user objects for participants.
    participants = UserSerializer(many=True, read_only=True)


    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'messages', 'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

        # For creating a conversation, you might need to handle participants differently
        # (e.g., allow writing only participant IDs).
        # If the requirement is just for display, read_only=True for participants is fine.
        # If for creation, you'd define a Writable Nested Serializer or use PrimaryKeyRelatedField.
        # For now, let's keep it read-only for simplicity based on the "nested relationships" prompt.

```
**Explanation:**

* **`UserSerializer`**: Exposes the key user information. `read_only_fields` ensures `id`, `user_id`, and `created_at` are not modifiable through the API, and are just displayed. We avoid directly exposing `password_hash` or a `password` field.
* **`MessageSerializer`**:
    * `sender = UserSerializer(read_only=True)`: This tells DRF to use the `UserSerializer` to represent the `sender` object. `read_only=True` means you can't set the sender directly when creating a message via this serializer; it's assumed to be set by the view logic (e.g., current authenticated user).
    * `conversation` field: We'll keep this as a simple ID field for now. When creating messages, the viewset will likely handle linking it to a specific `Conversation` instance.
* **`ConversationSerializer`**:
    * `messages = MessageSerializer(many=True, read_only=True)`: This is the key for nested messages. It tells DRF to fetch all messages related to this conversation (`related_name='messages'` on the `Message` model's `conversation` ForeignKey makes this possible) and serialize each of them using `MessageSerializer`. `many=True` is for a list of messages. `read_only=True` means you can't create messages by posting to the conversation endpoint; messages should be created through their own dedicated endpoint.
    * `participants = UserSerializer(many=True, read_only=True)`: Similar to messages, this displays the full details of the participating users.
