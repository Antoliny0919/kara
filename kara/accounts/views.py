from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm


def send_email_confirmation(request, user):
    pass


class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"

    def form_valid(self, form):
        self.user = form.save()

        return super().form_valid(form)


signup = SignupView.as_view()
