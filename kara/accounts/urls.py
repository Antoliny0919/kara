from allauth.account import views
from django.urls import path

urlpatterns = [
    path("login/", views.login, name="account_login"),
    path("signup/", views.signup, name="account_signup"),
]
