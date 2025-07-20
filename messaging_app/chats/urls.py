from django.urls import path, include
# CHANGE THIS LINE: Import the whole 'routers' module
from rest_framework import routers # Changed from 'from rest_framework.routers import DefaultRouter'
from .views import ConversationViewSet, MessageViewSet

# CHANGE THIS LINE: Instantiate using the full path
router = routers.DefaultRouter() # Now explicitly includes "routers."

# Register your ViewSets with the router
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]