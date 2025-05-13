from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    AuthenticationForm,
    BaseUserCreationForm,
    UserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from kara.base.forms import KaraForm, KaraModelForm
from kara.base.widgets import KaraTextInput

from .models import User
from .widgets import ProfileFileInput, StateBlock


class EmailVerificationCodeForm(KaraForm):
    code = forms.CharField(
        label=_("Confirmation Code"),
        max_length=6,
        help_text=_("Enter the 6-digit verification code sent to your email."),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop("code")
        super().__init__(*args, **kwargs)

    def compare_code(self, server, client):
        server_code = server.replace(" ", "").lower()
        client_code = client.replace(" ", "").lower()
        return server_code and server_code == client_code

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if not self.compare_code(server=self.code, client=code):
            self.add_error("code", _("The verification code does not match."))
        return code


class BaseCustomUserForm(KaraModelForm):
    bio_image = forms.ImageField(
        label=_("Profile Image"),
        help_text=_("If you want to change profile image, click on the image!"),
        widget=ProfileFileInput,
    )
    bio = forms.CharField(
        label=_("About Me"),
        widget=forms.Textarea,
        required=False,
    )
    email_confirmed = forms.BooleanField(
        label=_("Email Confirmed ?"),
        widget=StateBlock,
        required=False,
    )


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=KaraTextInput(
            attrs={"label": _("Username or Email"), "type": "text", "autofocus": True}
        )
    )
    password = forms.CharField(
        strip=False,
        widget=KaraTextInput(
            attrs={
                "label": _("Password"),
                "type": "password",
                "autocomplete": "current-password",
            }
        ),
    )


class UserProfileForm(BaseCustomUserForm):

    class Meta(BaseCustomUserForm):
        model = User
        fields = (
            "bio_image",
            "username",
            "email",
            "email_confirmed",
            "bio",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email_confirmed_state = kwargs["initial"]["email_confirmed"]
        if email_confirmed_state:
            self.fields["email_confirmed"].help_text = _(
                "You have verified your email."
            )
        else:
            self.fields["email_confirmed"].help_text = _(
                "You have not verified your email yet. "
                "Some features may be limited until you verify your email."
            )


class CustomUserCreationForm(UserCreationForm, KaraModelForm):

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )
        help_text = {
            "password2": _("Enter the same password as before, for verification.")
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def _post_clean(self):
        super(BaseUserCreationForm, self)._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password1", error)


class AccountDeleteForm(KaraForm):
    confirm_irrecoverable = forms.BooleanField(
        label=_("Deleted accounts cannot be recovered."),
        required=True,
    )
    confirm_data_loss = forms.BooleanField(
        label=_("Deleting your account will permanently remove all data."),
        required=True,
    )
