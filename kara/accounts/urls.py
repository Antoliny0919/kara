from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "email/confirmation/",
        views.EmailConfirmationView.as_view(),
        name="email_confirmation",
    ),
    path(
        "email/confirmation/resend/",
        views.ResendEmailVerificationCodeView.as_view(),
        name="email_confirmation_resend",
    ),
]
