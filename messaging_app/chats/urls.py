# messaging_app/chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet # Make sure these are imported correctly

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user') # <--- THIS IS CRUCIAL FOR /api/users/
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)), # <--- THIS IS CRUCIAL
]
""" from django.urls import path, include
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
] """



""" from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers # Changed from 'rest_framework' to 'rest_framework_nested'
from .views import ConversationViewSet, MessageViewSet

# Create a base router for top-level resources (e.g., conversations)
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet)

# Create a nested router for messages, nested under conversations
# This creates URLs like /conversations/{conversation_pk}/messages/
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-message')

# The API URLs are now determined automatically by the routers.
urlpatterns = [
    path('', include(router.urls)), # Includes top-level conversation URLs
    path('', include(conversations_router.urls)), # Includes nested message URLs
] """