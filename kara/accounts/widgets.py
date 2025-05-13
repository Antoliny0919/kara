from django.forms.widgets import CheckboxInput, ClearableFileInput


class ProfileFileInput(ClearableFileInput):
    template_name = "accounts/widgets/profile_file_input.html"


class StateBlock(CheckboxInput):
    template_name = "accounts/widgets/state_block.html"

    def render(self, name, value, attrs=None, renderer=None):
        state = bool(value)
        attrs["state"] = state
        return super().render(name, value, attrs, renderer)
