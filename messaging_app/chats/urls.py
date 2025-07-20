from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create a router instance
router = DefaultRouter()

# Register your ViewSets with the router
# The 'basename' argument is important if your queryset doesn't have a .model attribute,
# or if you want to explicitly name the set of URLs for reverse lookups.
# It's good practice to provide it.
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
