# chats/middleware/request_logger.py
import logging
from datetime import datetime
import os # Import os for settings.BASE_DIR
from django.conf import settings # Import settings

# --- IMPORTANT FIX FOR LOG FILE PATH ---
# Configure logging to write to requests.log in the project's BASE_DIR (root)
# This ensures requests.log is created in the same directory as manage.py
log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')
# If the logger already exists, get it, otherwise create it
# This prevents adding multiple handlers if the middleware is reloaded
logger = logging.getLogger('request_logger')
if not logger.handlers: # Add handler only if it doesn't already have one
    handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(message)s') # We format directly in __call__
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
# --- END IMPORTANT FIX ---


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Use the pre-configured logger
        self.logger = logger

    def __call__(self, request):
        user = request.user.username if request.user.is_authenticated else "Anonymous"
        self.logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        return self.get_response(request)