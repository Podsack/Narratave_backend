from django.urls import path
from .v1 import views as v1_view

urlpatterns = [
    path('signup/', v1_view.signup),
    path('login/', v1_view.login),
    path('user/', v1_view.get_user),
]
