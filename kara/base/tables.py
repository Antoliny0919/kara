from django_filters import FilterSet

from kara.wedding_gifts.filters import GiftSearchFilter

from .pagination import Pagination


class Table:
    # search_filter_class = None
    search_filter_class = GiftSearchFilter

    def __init__(self, request, model, base_queryset, list_per_page=0):
        self.model = model
        self.queryset = base_queryset
        self.list_per_page = list_per_page
        self.queryset = self.apply_search(request)
        self.result_objects = self.apply_pagination(request)

    def get_pagination_class(self, **kwargs):
        return Pagination

    def get_pagination(
        self,
        request,
        model,
        list_per_page,
        queryset,
    ):
        Pagination = self.get_pagination_class()
        return Pagination(request, model, list_per_page, queryset)

    def apply_search(self, request):
        if self.search_filter_class is not None:
            if not issubclass(self.search_filter_class, FilterSet):
                raise TypeError(
                    "search_filter_class attribute must be a subclass of `FilterSet`"
                )
            search_result = self.search_filter_class(
                request.GET, queryset=self.queryset
            )
            self.search_form = search_result.form
        return search_result.qs

    def apply_pagination(self, request):
        pagination = self.get_pagination(
            request, self.model, self.list_per_page, self.queryset
        )
        self.pagination = pagination
        return pagination.get_objects()
