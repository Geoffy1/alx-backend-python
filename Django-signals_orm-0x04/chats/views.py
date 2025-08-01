# Django-signals_orm-0x04/chats/views.py

from django.shortcuts import render, redirect
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
    return render(request, 'chats/home.html')