from django.urls import path

from .views_admin_freeze import FreezeAccountView, UnfreezeAccountView

urlpatterns = [
    path("freeze/", FreezeAccountView.as_view(), name="freeze_account"),
    path(
        "unfreeze/", UnfreezeAccountView.as_view(), name="unfreeze_account"
    ),
]

