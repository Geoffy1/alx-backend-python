# chats/middleware/role_permission.py
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group # Added for group checking

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths to protect that require admin or moderator role
        protected_paths = ['/api/messages/', '/api/conversations/']

        # Check if the current request path is one of the protected paths
        if any(path in request.path for path in protected_paths):
            user = request.user

            # Check if user is authenticated
            if not user.is_authenticated:
                return HttpResponseForbidden("Access denied. Authentication required.")

            # Check if user is superuser or belongs to 'Moderator' or 'Admin' group
            # Assuming 'is_moderator' attribute might not exist. Check groups instead.
            is_admin_or_moderator = user.is_superuser or \
                                    user.groups.filter(name='Admin').exists() or \
                                    user.groups.filter(name='Moderator').exists()

            if not is_admin_or_moderator:
                return HttpResponseForbidden("Access denied. Admins or moderators only.")

        return self.get_response(request)