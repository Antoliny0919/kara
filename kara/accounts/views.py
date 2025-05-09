import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, views as django_views
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, FormView, UpdateView, View

from .forms import (
    AccountDeleteForm,
    CustomAuthenticationForm,
    CustomUserCreationForm,
    EmailVerificationCodeForm,
    UserProfileForm,
)
from .models import User, UserProfile

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
        render_to_string("accounts/email/email_confirmation.txt", email_dict),
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=render_to_string(
            "accounts/email/email_confirmation.html", email_dict
        ),
        fail_silently=False,
    )
    register_pending_email_confirmation(request, email, username, verification_code)


def clear_confirmation_state(request):
    request.session.pop(PENDING_EMAIL_CONFIRMATION_SESSION_KEY, None)


class EmailConfirmationView(LoginRequiredMixin, FormView):
    form_class = EmailVerificationCodeForm
    template_name = "accounts/registration/email_confirmation.html"

    def dispatch(self, request, *args, **kwargs):
        self.verification = request.session.get(PENDING_EMAIL_CONFIRMATION_SESSION_KEY)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _("Email verification is complete!"),
        )
        return reverse("home")

    def form_valid(self, form):
        user = User.objects.get(username=self.verification.get("username"))
        user.profile.email_confirmed = True
        user.profile.save()
        clear_confirmation_state(self.request)
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
                "later_confirm_link": reverse("login"),
            }
        )
        return context


class ResendEmailVerificationCodeView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        send_user_confirmation_email(request, user)
        messages.add_message(
            request, messages.INFO, _("The email verification code has been resent.")
        )
        return redirect("email_confirmation")


@method_decorator(login_not_required, name="dispatch")
class LoginView(django_views.LoginView):
    form_class = CustomAuthenticationForm
    template_name = "accounts/registration/login.html"


class SignupView(FormView):
    form_class = CustomUserCreationForm
    template_name = "accounts/registration/signup.html"

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _(
                "Your registration was successful. Please check "
                "your email provided for a verification code."
            ),
        )
        return reverse("email_confirmation")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        send_user_confirmation_email(self.request, user)
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile.html"
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):
        """
        Populate the initial values for the UserProfile model fields used in the form.
        """
        initial = super().get_initial()
        profile = self.get_object().profile
        fields = self.get_form_class()._meta.fields
        user_profile_fields = {field.name for field in UserProfile._meta.fields}
        for field in fields:
            if field in user_profile_fields:
                initial[field] = getattr(profile, field, "")
        return initial

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _("Your profile has been updated!"),
        )
        return reverse("profile")

    def form_valid(self, form):
        user = form.save()
        profile = user.profile
        profile.bio_image = form.cleaned_data["bio_image"]
        profile.bio = form.cleaned_data["bio"]
        update_fields = ["bio_image", "bio"]
        # email is changed, the email verification status is also reset.
        if "email" in form.changed_data:
            profile.email_confirmed = False
            update_fields.append("email_confirmed")
        profile.save(update_fields=update_fields)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.get_object()
        kwargs["instance"] = user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.request.session
        # Restores the remembered modal(account_delete) state.
        account_delete_form_data = session.pop("account_delete_form_data", None)
        account_delete_modal_state = session.pop("account_delete_modal_state", False)
        context.update(
            {
                "account_delete_form": AccountDeleteForm(data=account_delete_form_data),
                "account_delete_modal_state": account_delete_modal_state,
            }
        )
        return context


class AccountDeleteView(DeleteView):
    form_class = AccountDeleteForm

    def get_object(self):
        return self.request.user

    def form_invalid(self, form):
        """
        When the form inside the modal fails,
        its current state is remembered so that it can be re-rendered.
        """
        self.request.session["account_delete_form_data"] = self.request.POST
        self.request.session["account_delete_modal_state"] = True
        return redirect("profile")

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _("Your account was successfully deleted."),
        )
        return reverse("home")
