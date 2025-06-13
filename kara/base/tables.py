from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.forms import CharField

from .forms import KaraForm
from .pagination import Pagination
from .widgets import KaraSearchInput


class TableSearchForm(KaraForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate "fields" dynamically because SEARCH_VAR is a variable:
        self.fields = {
            settings.SEARCH_VAR: CharField(
                required=False,
                strip=False,
                widget=KaraSearchInput(),
            ),
        }


class Table:
    pagination_class = Pagination
    search_form_class = TableSearchForm
    search_fields = []
    ordering = []
    columns = "__all__"

    def __init__(self, request, model, base_queryset, list_per_page=100):
        self.model = model
        self.opts = model._meta
        self.list_per_page = list_per_page
        if self.columns == "__all__":
            # Displays all model fields if columns are not specified
            self.columns = [
                field.name
                for field in self.opts.get_fields()
                if field.primary_key is not True
            ]
        search_form = self.search_form_class(request.GET)
        search_form.is_valid()
        self.search_form = search_form
        self.search_value = self.search_form.cleaned_data.get(settings.SEARCH_VAR) or ""
        self.params = dict(request.GET.lists())
        if settings.PAGE_VAR in self.params:
            del self.params[settings.PAGE_VAR]
        self.result_objects = self.get_queryset(request, base_queryset)

    def display_for_value(self, obj, column):
        """
        Determines the row value to be displayed in the table.
        You can apply various formatting to the row value based
        on the column type in this method.
        """
        return getattr(obj, column, "")

    def get_search_result(self, queryset, search_value):

        def construct_search(field_lookup):
            lookup_fields = field_lookup.split("__")
            prev_field = None
            for path_part in lookup_fields:
                try:
                    field = self.opts.get_field(path_part)
                    if not isinstance(
                        field,
                        (
                            models.CharField,
                            models.TextField,
                            models.ForeignKey,
                            models.OneToOneRel,
                            models.OneToOneField,
                        ),
                    ):
                        # Type checking is deferred for relational fields.
                        raise TypeError(
                            "Search logic only supports fields of type "
                            "`CharField` or `TextField`"
                            '("%s" field type is `%s`)'
                            % (field.name, field.__class__.__name__)
                        )
                except FieldDoesNotExist:
                    if prev_field and prev_field.get_lookup(path_part):
                        return field_lookup, True
                else:
                    prev_field = field
            # If no lookup is provided, icontains is used by default.
            return "%s__icontains" % field_lookup, False

        if self.search_fields and search_value:
            orm_lookups = []
            for field_lookup in self.search_fields:
                lookup = construct_search(field_lookup)
                orm_lookups.append(lookup)
            term_queries = []
            for orm_lookup in orm_lookups:
                lookup_field, have_lookup = orm_lookup
                if have_lookup:
                    lookup_value = lookup_field.split("__")[-1]
                    if lookup_value == "exact" or lookup_value == "iexact":
                        # If the lookup is exact or iexact,
                        # it returns objects that exactly match the given search value.
                        query = models.Q.create([(lookup_field, search_value)])
                        term_queries.append(query)
                        continue
                for word in search_value.split():
                    query = models.Q.create([(lookup_field, word)])
                    term_queries.append(query)
            # Combines the generated `Q` objects using OR.
            # This means that if search_fields contains multiple fields,
            # an object will be returned as long as it matches
            # the condition of any one field.
            queryset = queryset.filter(
                models.Q.create(term_queries, connector=models.Q.OR)
            )
        return queryset

    def columns_ordering(self, queryset):
        # Sorting prioritizes the field that was most recently selected.
        # The most recently selected field is at the end of the array,
        # and its order is reversed using [::-1]
        # so that it is applied with the highest priority.
        order_params = self.params.get(settings.ORDER_VAR, [])[::-1]
        ordered_queryset = queryset
        if order_params:
            ordered_queryset = queryset.order_by(*order_params)
        return ordered_queryset

    def get_pagination_result(self, request, queryset):
        pagination = self.pagination_class(
            request,
            queryset,
            self.list_per_page,
        )
        self.pagination = pagination
        return pagination.get_objects()

    def get_queryset(self, request, queryset):
        search_result = self.get_search_result(queryset, self.search_value)
        column_order_result = self.columns_ordering(search_result)
        pagination_result = self.get_pagination_result(request, column_order_result)
        return pagination_result
