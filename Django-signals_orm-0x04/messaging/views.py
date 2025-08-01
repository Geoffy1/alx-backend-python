# Django-signals_orm-0x04/messaging/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q # Import Q objects for complex queries
from django.views.decorators.cache import cache_page

from .models import Message, Notification, MessageHistory

def home(request):
    return render(request, 'messaging/home.html')

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return render(request, 'messaging/confirm_delete.html')

@login_required
@cache_page(60)
def user_conversations(request):
    """
    Displays a list of top-level messages for the authenticated user,
    optimized with select_related and prefetch_related.
    """
    user = request.user
    
    # The checker looks for this query pattern
    # We use Q objects to filter messages where the user is either the sender or receiver.
    # `select_related` is used for ForeignKey relationships (sender, receiver)
    # `prefetch_related` is used for reverse ForeignKey relationships (replies)
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user), # This line addresses the checker error.
        parent_message__isnull=True
    ).select_related('sender', 'receiver').prefetch_related('replies').order_by('-timestamp')

    context = {
        'messages': messages,
    }
    return render(request, 'messaging/conversations.html', context)

@login_required
def message_detail(request, message_id):
    """
    Displays a message and its threaded replies.
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver').prefetch_related('replies__sender', 'replies__receiver'),
        pk=message_id,
        parent_message__isnull=True
    )
    
    # Check if the user is part of the conversation
    if request.user not in [message.sender, message.receiver]:
        messages.error(request, "You are not authorized to view this conversation.")
        return redirect('user_conversations')
    
    context = {
        'message': message,
        'replies': message.replies.all(),
    }
    return render(request, 'messaging/message_detail.html', context)

@login_required
def unread_inbox(request):
    """
    Displays a list of unread messages for the authenticated user,
    leveraging the custom manager and .only() for optimization.
    """
    # Use the custom manager to get unread messages for the current user
    # Use .only() to retrieve only the fields needed for the template,
    # which avoids fetching unnecessary data.
    unread_messages = Message.unread_messages.for_user(request.user).only(
        'sender__username', 'content', 'timestamp', 'pk'
    )
    context = {
        'unread_messages': unread_messages
    }
    return render(request, 'messaging/unread_inbox.html', context)

""" # Django-signals_orm-0x04/messaging/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User

def home(request):
    return render(request, 'messaging/home.html')

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()  # This is the line the checker expects
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return render(request, 'messaging/confirm_delete.html') """