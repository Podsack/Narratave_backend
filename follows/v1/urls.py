from django.urls import path
from .views import follow_user, unfollow_user, get_follow_info, followings_list

urlpatterns = [
    path('follow/', follow_user),
    path('unfollow/', unfollow_user),
    path('with-user/<int:related_user_id>/', get_follow_info),
    path('followings-by-latest/', followings_list)
]
