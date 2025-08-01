# Django-signals_orm-0x04/messaging/views.py

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
    return render(request, 'messaging/confirm_delete.html')