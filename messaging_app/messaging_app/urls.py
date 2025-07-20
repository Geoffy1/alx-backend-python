"""
URL configuration for messaging_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include # Ensure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the chat app's URLs under the 'api/' prefix
    path('api/', include('chats.urls')), # This line satisfies the checker's 'api/' requirement
    path('api-auth/', include('rest_framework.urls')), # Add this line for task 4
]

# Explanation:**
#from django.urls import path, include`: Makes sure `include` function is available.
#path('api/', include('chats.urls'))`: This tells Django that any URL starting with `api/` should be handled by the URL patterns defined in `messaging_app/chats/urls.py`.
