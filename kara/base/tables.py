from .pagination import Pagination


class Table:
    def __init__(self, request, model, base_queryset, list_per_page=0):
        self.model = model
        self.queryset = base_queryset
        self.list_per_page = list_per_page
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

    def apply_pagination(self, request):
        pagination = self.get_pagination(
            request, self.model, self.list_per_page, self.queryset
        )
        self.pagination = pagination
        return pagination.get_objects()
