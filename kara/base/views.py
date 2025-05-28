from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseCreateView, FormMixin, ModelFormMixin

from .utils import pascal_to_snake


class PartialTemplateResponseMixin(TemplateResponseMixin):
    partial_template_identifier = None

    def get_template_names(self):
        if self.request.htmx:
            if self.template_name is None or self.partial_template_identifier is None:
                raise ImproperlyConfigured(
                    "PartialTemplateResponseMixin requires either a definition of "
                    "'template_name' and 'partial_template_identifier' or "
                    "an implementation of 'get_template_names()'"
                )
            else:
                partial_template_name = (
                    self.template_name + self.partial_template_identifier
                )
                return [partial_template_name]
        else:
            return super().get_template_names()


class PartialTemplateFormMixin(FormMixin):

    @cached_property
    def form_name(self):
        # Convert PascalCase form name to snake_case.
        # To use a unified form_name across multiple forms,
        # define it in the parent class(overwrite).
        name = self.form_class.__name__
        form_name = pascal_to_snake(name)
        return form_name

    def get_context_data(self, **kwargs):
        context = ContextMixin().get_context_data(**kwargs)
        if self.form_name not in kwargs or kwargs[self.form_name] is None:
            # If no form is provided, a new one will be created.
            context[self.form_name] = self.form_class()
        return context

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(**{self.form_name: form}))


class PartialTemplateModelFormMixin(PartialTemplateFormMixin, ModelFormMixin):

    def reuse_form(self, form):
        """
        You can reuse the form used during template rendering to create a new form.
        Override this in a subclass to return a Form instance.
        """
        return None

    def form_valid(self, form):
        self.object = form.save()
        new_form = self.reuse_form(form)
        return self.render_to_response(
            self.get_context_data(**{self.form_name: new_form})
        )


class PartialTemplateBaseCreateView(PartialTemplateModelFormMixin, BaseCreateView):
    pass


class PartialTemplateCreateView(
    PartialTemplateResponseMixin, PartialTemplateBaseCreateView
):
    pass


class PartialTemplateDetailView(PartialTemplateResponseMixin, DetailView):
    pass
