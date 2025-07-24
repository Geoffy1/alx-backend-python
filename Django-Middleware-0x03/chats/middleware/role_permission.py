# chats/middleware/role_permission.py
from django.http import HttpResponseForbidden

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = ['/api/messages/', '/api/conversations/']
        if any(path in request.path for path in protected_paths):
            user = request.user
            if not user.is_authenticated or not (user.is_superuser or getattr(user, 'is_moderator', False)):
                return HttpResponseForbidden("Access denied. Admins or moderators only.")
        return self.get_response(request)

