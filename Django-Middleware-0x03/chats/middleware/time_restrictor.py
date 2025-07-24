# chats/middleware/time_restrictor.py
from django.http import HttpResponseForbidden
from datetime import datetime

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if not (18 <= current_hour <= 21):
            return HttpResponseForbidden("Access not allowed at this time.")
        return self.get_response(request)

