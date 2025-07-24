# Django-Middleware-0x03/chats/middleware.py

import logging
from datetime import datetime
from django.conf import settings
import os
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict
from django.contrib.auth.models import Group

# Configure logging for requests
log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')

# Ensure the log file exists and is writable
try:
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'a') as f:
            f.write('') # Create the file if it doesn't exist
except IOError as e:
    print(f"Error creating or accessing requests.log: {e}")
    # Handle this more gracefully in a real application, e.g., by falling back to console logging

request_logger = logging.getLogger('request_logger')
request_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file_path)
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
request_logger.addHandler(file_handler)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before the view
        # Get user information
        user = 'AnonymousUser'
        if request.user.is_authenticated:
            user = request.user.username
        elif hasattr(request, 'user') and request.user.is_anonymous:
             user = 'AnonymousUser'

        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        request_logger.info(log_message)

        response = self.get_response(request)

        # Process response after the view (optional for this task, but good practice)
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        # Define the allowed time window: between 6 AM (06:00) and 9 PM (21:00)
        # Note: The prompt states "outside 9PM and 6PM". I will assume it means outside 9 PM and 6 AM.
        # If it truly meant "outside 9 PM and 6 PM", please clarify.
        # I'll interpret "outside 9PM and 6PM" as meaning restricted between 9PM and 6AM.
        # So, allowed hours are 6:00 to 21:00.

        # Correct interpretation for "outside 9PM and 6AM":
        # Access is DENIED if current time is >= 21:00 (9 PM) OR < 6:00 (6 AM)
        if not (datetime.strptime("06:00", "%H:%M").time() <= now < datetime.strptime("21:00", "%H:%M").time()):
            return HttpResponseForbidden("Access to chat is restricted outside 6 AM and 9 PM.")

        response = self.get_response(request)
        return response

# Store IP request counts and timestamps
# Structure: {ip_address: [(timestamp1, count1), (timestamp2, count2), ...]}
# This simple structure will store each request's timestamp.
# We'll then filter out old requests to count within the window.
request_timestamps = defaultdict(list)
RATE_LIMIT_MESSAGES = 5
RATE_LIMIT_WINDOW_SECONDS = 60 # 1 minute

class OffensiveLanguageMiddleware: # Renamed for clarity, you can use OffensiveLanguageMiddleware
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/chats/messages'): # Assuming chat messages are POSTed to /chats/messages or similar
            ip_address = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR')
            if not ip_address:
                # If IP cannot be determined, proceed with caution or block
                return HttpResponseForbidden("Could not determine IP address for rate limiting.")

            current_time = time.time()

            # Clean up old requests
            # Remove timestamps older than the window
            request_timestamps[ip_address] = [
                t for t in request_timestamps[ip_address]
                if t > current_time - RATE_LIMIT_WINDOW_SECONDS
            ]

            # Check if the user has exceeded the limit
            if len(request_timestamps[ip_address]) >= RATE_LIMIT_MESSAGES:
                return HttpResponseForbidden(f"You have exceeded the message limit of {RATE_LIMIT_MESSAGES} messages per {RATE_LIMIT_WINDOW_SECONDS} seconds. Please try again later.")

            # If within limit, record the current request
            request_timestamps[ip_address].append(current_time)

        response = self.get_response(request)
        return response

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define paths that require admin or moderator roles
        # Adjust these paths to match your application's needs
        restricted_paths = [
            '/admin/',
            '/chats/moderate/', # Example path for moderator actions
            # Add other paths that should only be accessible by specific roles
        ]

        # Check if the current request path is in our restricted list
        if any(request.path.startswith(path) for path in restricted_paths):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Access denied: You must be logged in.")

            is_admin = request.user.is_staff or request.user.is_superuser
            # Check if user belongs to 'Moderator' group
            is_moderator = request.user.groups.filter(name='Moderator').exists()

            if not (is_admin or is_moderator):
                return HttpResponseForbidden("Access denied: You do not have the required role (Admin or Moderator).")

        response = self.get_response(request)
        return response