from django.forms.widgets import CheckboxInput, ClearableFileInput, Input, Textarea


class FloatingLabelInput(Input):
    template_name = "accounts/widgets/floating_label_input.html"


class FloatingLabelTextarea(Textarea):
    template_name = "accounts/widgets/floating_label_textarea.html"


class BooleanStateBlock(CheckboxInput):
    template_name = "accounts/widgets/boolean_state_block.html"

    def render(self, name, value, attrs=None, renderer=None):
        state = bool(value)
        attrs["state"] = state
        return super().render(name, value, attrs, renderer)


class ProfileFileInput(ClearableFileInput):
    template_name = "accounts/widgets/profile_file_input.html"
