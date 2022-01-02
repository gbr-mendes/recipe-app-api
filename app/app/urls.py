from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    # API URL's
    path('api/user/', include('users.urls')),
]
