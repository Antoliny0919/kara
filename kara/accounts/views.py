import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import FormView

from .forms import CustomUserCreationForm, EmailVerificationCodeForm
from .models import User

PENDING_EMAIL_CONFIRMATION_SESSION_KEY = "pending_email_confirmation"


def generate_code():
    forbidden_chars = "0OI18B2ZAEU"
    allowed_chars = string.ascii_uppercase + string.digits
    for ch in forbidden_chars:
        allowed_chars = allowed_chars.replace(ch, "")
    return get_random_string(length=6, allowed_chars=allowed_chars)


def register_pending_email_confirmation(request, email, username, code):
    request.session[PENDING_EMAIL_CONFIRMATION_SESSION_KEY] = {
        "username": username,
        "email": email,
        "code": code,
    }


def send_user_confirmation_email(request, user):
    verification_code = generate_code()
    email = user.email
    username = user.username
    email_dict = {
        "code": verification_code,
        "name": username,
    }
    send_mail(
        "Kara Email Confirmation",
        render_to_string("emails/email_confirmation.txt", email_dict),
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=render_to_string("emails/email_confirmation.html", email_dict),
        fail_silently=False,
    )
    register_pending_email_confirmation(request, email, username, verification_code)


def clear_confirmation_state(request):
    request.session.pop(PENDING_EMAIL_CONFIRMATION_SESSION_KEY, None)


class SignupView(FormView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            "Your registration was successful. Please check "
            "your email provided for a confirmation link.",
        )
        return reverse("email_confirmation")

    def form_valid(self, form):
        user = form.save()
        send_user_confirmation_email(self.request, user)
        return super().form_valid(form)


class EmailConfirmationView(FormView):
    form_class = EmailVerificationCodeForm
    template_name = "registration/email_confirmation.html"

    def dispatch(self, request, *args, **kwargs):
        self.verification = request.session.get(PENDING_EMAIL_CONFIRMATION_SESSION_KEY)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            "Email verification is complete!",
        )
        return reverse("home")

    def form_valid(self, form):
        user = User.objects.get(username=self.verification.get("username"))
        user.profile.email_confirmed = True
        user.profile.save()
        clear_confirmation_state(self.request)
        login(self.request, user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["code"] = self.verification.get("code")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "email": self.verification.get("email"),
            }
        )
        return context
