# messaging_app/chats/filters.py
import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter by conversation ID
    conversation = django_filters.UUIDFilter(field_name='conversation__conversation_id', lookup_expr='exact')
    # Filter by sender's user_id (UUID)
    sender = django_filters.UUIDFilter(field_name='sender__id', lookup_expr='exact')
    # Filter messages sent after a specific datetime
    sent_at_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    # Filter messages sent before a specific datetime
    sent_at_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'sent_at_after', 'sent_at_before']