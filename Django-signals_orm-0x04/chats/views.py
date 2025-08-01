# Django-signals_orm-0x04/chats/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from messaging.models import Message, Notification, MessageHistory # Import Message
from django.db.models import F # For Task 4 optimization

@login_required
def delete_user_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return render(request, 'chats/confirm_delete.html')

def home(request):
    return render(request, 'chats/home.html')

@login_required
def conversation_list(request):
    # Fetch top-level messages (those without a parent) efficiently
    # Use select_related for sender and receiver to avoid N+1 queries for user info
    # Use prefetch_related for replies to get all replies in one go for each message
    messages = Message.objects.filter(parent_message__isnull=True).select_related('sender', 'receiver').prefetch_related('replies')

    # For displaying threaded replies, you'd typically iterate through the messages
    # and then iterate through their `instance.replies.all()` in the template.
    # The prefetch_related makes subsequent access to `replies` hit the cache, not the DB.

    context = {
        'messages': messages
    }
    return render(request, 'chats/conversation_list.html', context)

@login_required
def message_detail(request, message_id):
    # Fetch the main message and all its replies, including nested replies
    # This example shows how to get all replies. For deep recursion, you might
    # need custom logic or a third-party package for very complex threading.
    # For now, we'll fetch the main message and its direct replies, then prefetch their replies.
    # For truly recursive fetching using ORM, it's more complex and often involves raw SQL
    # or specific libraries. The prefetch_related will handle direct replies efficiently.

    # To get a more "recursive" structure with ORM, you often do it in steps or
    # build a tree in Python after fetching.
    main_message = get_object_or_404(Message.objects.select_related('sender', 'receiver'), pk=message_id)

    # Prefetch all direct replies and their senders/receivers
    # For deeper nesting, prefetch_related can be chained or used with `Prefetch` object.
    # Example: .prefetch_related(Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver').prefetch_related('replies')))
    # This simple prefetch will fetch direct replies only.
    replies = main_message.replies.all().select_related('sender', 'receiver')


    # To truly represent a tree, you'd usually fetch all relevant messages and then
    # build the tree structure in Python. For simplicity, we'll display direct replies.

    context = {
        'main_message': main_message,
        'replies': replies,
    }
    return render(request, 'chats/message_detail.html', context)
# Django-signals_orm-0x04/chats/views.py

""" from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User

@login_required
def delete_user_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request) # Log out the user before deleting
        user.delete() # This will trigger the post_delete signal on User model
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home') # Redirect to a homepage or login page
    return render(request, 'chats/confirm_delete.html') # A template for confirmation

def home(request):
    return render(request, 'chats/home.html') """