# messaging_app/chats/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

# Get the custom User model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'created_at']
        read_only_fields = ['id', 'email', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    # 'participants' is a read-only field that will use UserSerializer to display member details
    # 'member_ids' is a write-only field used for creating/updating conversation members by their IDs
    participants = UserSerializer(many=True, read_only=True) # Match model's 'participants' field
    member_ids = serializers.ListField(
        child=serializers.UUIDField(), # Assuming your User IDs are UUIDs
        write_only=True,
        required=True # member_ids is required when creating a conversation
    )

    class Meta:
        model = Conversation
        # Ensure all fields from your Conversation model are listed here if you want them
        fields = ['conversation_id', 'title', 'participants', 'member_ids', 'created_at'] # Match model's 'conversation_id' and 'title'
        read_only_fields = ['conversation_id', 'created_at']

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids') # This is correct, as member_ids is for participants, not a direct model field
        
        # --- NEW ADDITION/CHANGE HERE ---
        # Explicitly filter validated_data to include only model fields
        # This prevents unexpected keyword arguments like 'request' from being passed to the model
        model_fields = [field.name for field in Conversation._meta.get_fields()]
        conversation_data = {k: v for k, v in validated_data.items() if k in model_fields}
        
        conversation = Conversation.objects.create(**conversation_data) # Use filtered data
        # --- END NEW ADDITION/CHANGE ---
        
        current_user = self.context['request'].user
        conversation.participants.add(current_user)

        for member_id in member_ids:
            try:
                member = User.objects.get(id=member_id)
                conversation.participants.add(member)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"member_ids": f"User with ID {member_id} does not exist."}
                )
        
        return conversation
    
    def update(self, instance, validated_data):
        # Logic to handle updating participants if needed for PATCH/PUT requests
        member_ids = validated_data.pop('member_ids', None)
        
        # Update regular fields (e.g., 'title')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if member_ids is not None:
            # Clear existing participants and add new ones
            instance.participants.clear() # Use 'participants' field
            current_user = self.context['request'].user
            instance.participants.add(current_user) # Ensure creator is still a member
            
            for member_id in member_ids:
                try:
                    member = User.objects.get(id=member_id)
                    instance.participants.add(member) # Use 'participants' field
                except User.DoesNotExist:
                    raise serializers.ValidationError(
                        {"member_ids": f"User with ID {member_id} does not exist."}
                    )
        
        return instance


class MessageSerializer(serializers.ModelSerializer):
    # Read-only field to display sender's details
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        # Match model's 'message_id', 'message_body', and 'sent_at'
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at'] # conversation and sender will be set programmatically

    def create(self, validated_data):
        # 'conversation' field is usually passed in the URL or context, not direct validated_data
        # 'sender' is the current authenticated user, obtained from request context
        
        # Ensure conversation instance is passed via context if it's not in validated_data
        conversation_id = self.context.get('view').kwargs.get('conversation_pk')
        if not conversation_id:
            raise serializers.ValidationError("Conversation ID is required.")

        try:
            # Match model's primary key name 'conversation_id'
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation not found.")

        validated_data['conversation'] = conversation
        validated_data['sender'] = self.context['request'].user
        
        return super().create(validated_data)