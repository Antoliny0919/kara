from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "email/confirmation/",
        views.EmailConfirmationView.as_view(),
        name="email_confirmation",
    ),
]
