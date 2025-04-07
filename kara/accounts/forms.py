from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    AuthenticationForm,
    BaseUserCreationForm,
    SetPasswordMixin,
    UserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User
from .widgets import FloatingLabelInput


class EmailVerificationCodeForm(forms.Form):
    code = forms.CharField(
        widget=FloatingLabelInput(attrs={"label": _("Confirmation Code")}),
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


class CustomSetPasswordMixin(SetPasswordMixin):
    @staticmethod
    def create_password_fields(label1=_("Password"), label2=_("Password confirmation")):
        password = forms.CharField(
            required=True,
            strip=False,
            widget=FloatingLabelInput(
                attrs={
                    "label": label1,
                    "type": "password",
                    "autocomplete": "new-password",
                }
            ),
            help_text=password_validation.password_validators_help_text_html(),
        )
        password_confirmation = forms.CharField(
            label=label2,
            required=True,
            widget=FloatingLabelInput(
                attrs={
                    "label": label2,
                    "type": "password",
                    "autocomplete": "new-password",
                }
            ),
            strip=False,
            help_text=_("Enter the same password as before, for verification."),
        )
        return password, password_confirmation


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=FloatingLabelInput(
            attrs={"label": _("Username or Email"), "type": "text", "autofocus": True}
        )
    )
    password = forms.CharField(
        strip=False,
        widget=FloatingLabelInput(
            attrs={
                "label": _("Password"),
                "type": "password",
                "autocomplete": "current-password",
            }
        ),
    )


class CustomUserCreationForm(UserCreationForm, forms.ModelForm):
    username = forms.CharField(
        min_length=4,
        widget=FloatingLabelInput(
            attrs={"label": _("Username"), "type": "text", "autocomplete": "username"}
        ),
    )
    email = forms.EmailField(
        widget=FloatingLabelInput(
            attrs={
                "label": _("Email"),
                "type": "email",
                "autocomplete": "email",
            }
        )
    )
    password1, password2 = CustomSetPasswordMixin.create_password_fields()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

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
