# chats/middleware/time_restrictor.py
from django.http import HttpResponseForbidden
from datetime import datetime

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Task states 9PM and 6PM. Interpreting as between 6PM (18h) and 9PM (21h) inclusive.
        if not (18 <= current_hour <= 21):
            return HttpResponseForbidden("Access not allowed at this time.")
        return self.get_response(request)