from django.urls import path
from .views import register, user_list, user_detail

urlpatterns = [
    path('register/', register, name='register'),
    path('users/', user_list, name='user_list'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
] 