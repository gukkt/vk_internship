from django.urls import path

from user.views import user_detail, user_create

urlpatterns = [
    path('users/', user_create, name='user_detail'),
    path('users/<int:user_id>/', user_detail, name='user_create'),
]
