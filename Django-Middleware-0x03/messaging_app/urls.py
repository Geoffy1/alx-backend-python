# messaging_app/messaging_app/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls), # Django Admin panel
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Get new token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh token
    path('api/', include('chats.urls')), # <--- Include your app's API URLs under /api/
]