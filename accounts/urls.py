from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("create/", views.CreateAccountView.as_view(), name="create"),
    path("token/", views.CreateTokenView.as_view(), name="token"),
    path("me/", views.ManageUserView.as_view(), name="me"),
]
