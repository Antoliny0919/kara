import inspect

from django.forms import Form, ModelForm

from .widgets import (
    KaraCheckboxInput,
    KaraEmailInput,
    KaraNumberInput,
    KaraPasswordInput,
    KaraRadioSelect,
    KaraSplitDateInput,
    KaraTextarea,
    KaraTextInput,
)


class ConvertWidgetMixin:

    widgets_map = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            self.convert_to_widget(field)

    def convert_to_widget(self, field):
        """
        It converts a widget with a specific name to a
        widget registered in widgets_map.
        """
        widget = field.widget
        widget_class_name = widget.__class__.__name__
        kara_widget_cls = self.widgets_map.get(widget_class_name)
        if kara_widget_cls is not None:
            params = self.get_widget_init_params(kara_widget_cls, field)
            field.widget = kara_widget_cls(**params)

    def get_widget_init_params(self, replace_widget_cls, field):
        params = {}
        # Retrieve the initialization parameters of the new replacement widget.
        signature = inspect.signature(replace_widget_cls.__init__)
        for name, _ in signature.parameters.items():
            if name == "self":
                continue
            # Retrieve the attributes to pass to the replacement widget
            # from the existing field or its widget.
            params[name] = getattr(field.widget, name, None) or getattr(
                field, name, None
            )
        return params


class KaraWidgetMixin(ConvertWidgetMixin):

    widgets_map = {
        "TextInput": KaraTextInput,
        "EmailInput": KaraEmailInput,
        "PasswordInput": KaraPasswordInput,
        "NumberInput": KaraNumberInput,
        "Textarea": KaraTextarea,
        "RadioSelect": KaraRadioSelect,
        "CheckboxInput": KaraCheckboxInput,
        "DateInput": KaraSplitDateInput,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            self.add_label_to_widget(field)

    def add_label_to_widget(self, field):
        """
        The kara widgets stores the label value in ``widget.attrs.label``
        So you can access it in the template via {{ widget.attrs.label }}.
        """
        field.widget.attrs["label"] = field.label or ""


class KaraForm(KaraWidgetMixin, Form):
    pass


class KaraModelForm(KaraWidgetMixin, ModelForm):
    pass
