from django.urls import path

from friendship.views import FriendshipStatusView, FriendshipRequestsView, FriendshipsListView, \
    FriendshipRequestsListView, DeleteFriendView

urlpatterns = [
    path('friendships/requests/<int:user_id>-<int:target_user_id>/<str:action>/', FriendshipRequestsView.as_view(), name='new_friendship_request'),
    path('friendships/requests/<int:user_id>/<str:requests_type>/', FriendshipRequestsListView.as_view(), name='new_friendship_request'),
    path('friendships/delete/<int:user_id>-<int:target_user_id>/', DeleteFriendView.as_view(), name='delete_friendship'),
    path('friendships/status/<int:user_id>-<int:target_user_id>/', FriendshipStatusView.as_view(), name='friendship_status'),
    path('friendships/<int:user_id>/', FriendshipsListView.as_view(), name='friendships_list'),
]
