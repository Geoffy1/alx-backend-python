# chats/middleware/rate_limiter.py
from django.http import JsonResponse
from time import time

class OffensiveLanguageMiddleware: # Class name is OffensiveLanguageMiddleware as per prompt
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_log = {}  # {ip: [timestamps]}

    def __call__(self, request):
        if request.method == 'POST' and '/messages/' in request.path:
            ip = request.META.get('REMOTE_ADDR')
            now = time()
            window = 60  # seconds
            max_requests = 5

            self.request_log.setdefault(ip, [])
            # Remove timestamps older than 1 minute
            self.request_log[ip] = [ts for ts in self.request_log[ip] if now - ts < window]

            if len(self.request_log[ip]) >= max_requests:
                return JsonResponse({'error': 'Rate limit exceeded. Max 5 messages/min.'}, status=429)

            self.request_log[ip].append(now)
        return self.get_response(request)