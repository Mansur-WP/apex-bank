from django.urls import path
from .views import ProfileView, ChangePasswordView

urlpatterns = [
    path("",          ProfileView.as_view(),         name="profile"),
    path("password/", ChangePasswordView.as_view(),  name="change_password"),
]
