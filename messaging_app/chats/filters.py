# messaging_app/chats/filters.py
import django_filters
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageFilter(django_filters.FilterSet):
    # Filter messages by participant username in the associated conversation
    # Example usage: /messages/?participant_username=john_doe
    participant_username = django_filters.CharFilter(
        field_name='conversation__participants__username',
        lookup_expr='iexact', # Case-insensitive exact match
        label='Filter by participant username (case-insensitive)'
    )

    # Filter messages by a list of participant IDs in the associated conversation
    # Example usage: /messages/?participant_id=1&participant_id=2
    participant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='conversation__participants__id',
        to_field_name='id', # Specifies that the input value is the 'id' field of the User model
        label='Filter by participant ID(s)'
    )

    # Filter messages within a time range (start date/time)
    # Example usage: /messages/?start_date=2025-01-01T00:00:00Z
    start_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='gte') # Greater than or equal to

    # Filter messages within a time range (end date/time)
    # Example usage: /messages/?end_date=2025-12-31T23:59:59Z
    end_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='lte') # Less than or equal to

    # Filter messages by a specific conversation ID
    # Example usage: /messages/?conversation=5
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation__id',
        label='Filter by Conversation ID'
    )

    class Meta:
        model = Message
        # Define the fields available for filtering
        fields = ['participant_username', 'participant_id', 'start_date', 'end_date', 'conversation']