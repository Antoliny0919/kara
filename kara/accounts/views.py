import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, views as django_views
from django.contrib.auth.decorators import login_not_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, UpdateView, View

from .forms import (
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
        render_to_string("emails/email_confirmation.txt", email_dict),
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=render_to_string("emails/email_confirmation.html", email_dict),
        fail_silently=False,
    )
    register_pending_email_confirmation(request, email, username, verification_code)


def clear_confirmation_state(request):
    request.session.pop(PENDING_EMAIL_CONFIRMATION_SESSION_KEY, None)


@method_decorator(login_required, name="dispatch")
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


class SignupView(FormView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"

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


class ProfileView(UpdateView):
    template_name = "accounts/profile.html"
    form_class = UserProfileForm
    model = UserProfile
    url_kwarg = "username"

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            raise PermissionDenied(
                "You do not have permission to edit %s's profile" % obj.user.username
            )
        return super().post(request, *args, **kwargs)

    def get_object(self):
        queryset = self.get_queryset()
        username = self.kwargs.get(self.url_kwarg)
        if username is None:
            raise AttributeError(
                "%s must be called with a %s parameter in the URLconf."
                % (self.__class__.__name__, self.url_kwarg)
            )
        queryset = queryset.filter(user__username=username)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("%s user does not exist." % username)
        return obj

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _("Your profile has been updated!"),
        )
        return reverse("profile", args=(self.kwargs.get(self.url_kwarg),))

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
        profile = self.get_object()
        user = profile.user
        kwargs["instance"] = user
        kwargs["initial"] = {
            "username": user.username,
            "email": user.email,
            "bio": profile.bio,
            "bio_image": profile.bio_image,
            "email_confirmed": profile.email_confirmed,
        }
        return kwargs
