from django.contrib import messages
from django.urls import reverse
from django.views.generic import FormView

from .forms import CustomUserCreationForm


def send_user_confirmation_email():
    pass


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
        return reverse("signup")

    def form_valid(self, form):
        form.save()
        send_user_confirmation_email()
        return super().form_valid(form)
