from django.urls import path
import authentication.v1.views as v1_view

urlpatterns = [
    path('signup/', v1_view.signup),
    path('login/', v1_view.login),
    path('user/', v1_view.get_user),
    path('refresh-token/', v1_view.refresh_access_token),
    path('logout/', v1_view.logout),
    path('google-signin/', v1_view.login_with_google),
]
