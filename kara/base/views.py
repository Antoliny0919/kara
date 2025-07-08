from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseCreateView, FormMixin, ModelFormMixin

from .pagination import Pagination
from .utils import pascal_to_snake


class PartialTemplateResponseMixin(TemplateResponseMixin):

    def get_template_names(self):
        if self.request.htmx:
            htmx_target = self.request.headers.get("Hx-Target", None)
            if self.template_name is None or htmx_target is None:
                raise ImproperlyConfigured(
                    "PartialTemplateResponseMixin requires 'template_name' to be "
                    "defined and the request must include an 'Hx-Target' header."
                )
            else:
                partial_template_name = self.template_name + f"#{htmx_target}"
                return [partial_template_name]
        else:
            return super().get_template_names()


class PartialTemplateFormMixin(FormMixin):

    @cached_property
    def form_name(self):
        for cls in self.__class__.__mro__:
            # Class attribute form_name takes precedence
            if "form_name" in cls.__dict__ and isinstance(
                cls.__dict__["form_name"], str
            ):
                return cls.form_name
        # If form_name is not explicitly set,
        # it defaults to the snake_case version of the form class name
        name = self.form_class.__name__
        return pascal_to_snake(name)

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


class MultipleObjectMixin(ContextMixin):
    """
    A modified version of Django's ListView that supports multiple models.

    paginate:
        Specifies the models to apply pagination to.
        Use the model name as the key to define list_per_page and page_kwarg.
        e.g. CashGift(models.Model)
        - paginate = {"cashgift"(CashGift._meta.model_name): {"list_per_page": 10, "page_kwarg": "gift_p"}} # noqa

    context_object_name:
        Determines the context variable name for a specific model.
        e.g. InKindGift(models.Model)
        - context_object_name = {"inkindgift"(InKindGift._meta.model_name): "in_kind_gifts"} # noqa
        Allows access to the queryset of the InKindGift model in the template
        using the name in_kind_gifts.
    """

    queryset = None
    model = None
    pagination_class = Pagination
    paginate = {}
    context_object_name = {}

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.

        Unlike the default Django ListView, allows multiple models.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
            elif isinstance(queryset, (list, tuple)):
                queryset = [q.all() for q in queryset]
        elif self.model is not None:
            if isinstance(self.model, (list, tuple)):
                queryset = [m._default_manager.all() for m in self.model]
            else:
                queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )
        return queryset

    def get_pagination(self, request, queryset, list_per_page, page_var):
        return self.pagination_class(request, queryset, list_per_page, page_var)

    def paginate_queryset(self, queryset, list_per_page, page_var):
        data = {}
        key = self.get_context_object_name(queryset.model)
        page_var = page_var if page_var is not None else f"{key}_page"
        pagination = self.get_pagination(
            self.request, queryset, list_per_page, page_var
        )
        data[key] = pagination.get_objects()
        # Pagination object can be accessed using context_name + '_pagination'.
        data[f"{key}_pagination"] = pagination
        return data

    def get_context_object_name(self, model):
        """
        The `get_context_object_name` method looks up the value using the
        model_name of the given model as the key.
        In other words, the dictionary keys in `context_object_name` must
        match the model_name of the models you want to apply it to.
        """
        model_name = model._meta.model_name
        if model_name in self.context_object_name:
            return self.context_object_name[model_name]
        else:
            return "%s_list" % model_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # object_list must be set get method.
        queryset = self.object_list
        if not isinstance(queryset, (list, tuple)):
            queryset = [queryset]
        for q in queryset:
            model_name = q.model._meta.model_name
            if model_name in self.paginate:
                # When looking up values in the paginate attribute,
                # the lookup is based on the model's model_name.
                # In other words, models you want to paginate must have a
                # corresponding key in paginate matching their model_name.
                paginate = self.paginate[model_name]
                data = self.paginate_queryset(
                    q,
                    paginate["list_per_page"],
                    paginate.get("page_var", None),
                )
                context.update(data)
            else:
                context[self.get_context_object_name(q.model)] = q
        return context


class BaseListView(MultipleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)


class PartialTemplateListView(PartialTemplateResponseMixin, BaseListView):
    pass


class PartialTemplateBaseCreateView(PartialTemplateModelFormMixin, BaseCreateView):
    pass


class PartialTemplateCreateView(
    PartialTemplateResponseMixin, PartialTemplateBaseCreateView
):
    pass


class PartialTemplateDetailView(PartialTemplateResponseMixin, DetailView):
    pass
