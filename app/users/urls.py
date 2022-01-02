from django.urls import path

from . import views


app_name = "users"

urlpatterns = [
    path('create/', views.CreateUserAPIView.as_view(), name="create"),
    path('token/', views.CreateTokenView.as_view(), name='token'),
]
