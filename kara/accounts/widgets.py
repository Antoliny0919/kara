from django.forms.widgets import Input


class FloatingLabelInput(Input):
    template_name = "accounts/widgets/floating_label_input.html"
