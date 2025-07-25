from django.core.paginator import InvalidPage, Paginator

from .exceptions import IncorectLookupParameter


class Pagination:
    def __init__(
        self,
        request,
        queryset,
        list_per_page,
        page_var="page",
    ):
        self.queryset = queryset
        model = queryset.model
        self.model = model
        self.opts = model._meta
        self.list_per_page = list_per_page
        self.page_var = page_var
        try:
            # Get the current page from the query string.
            self.page_num = int(request.GET.get(self.page_var, 1))
        except ValueError:
            self.page_num = 1
        self.params = request.GET.copy()
        self.setup()

    @property
    def page_range(self):
        return (
            self.paginator.get_elided_page_range(self.page_num)
            if self.multi_page
            else []
        )

    def get_paginator_class(self, **kwargs):
        return Paginator

    def get_paginator(
        self,
        queryset,
        per_page,
        orphans=0,
        allow_empty_first_page=True,
    ):
        Paginator = self.get_paginator_class()
        return Paginator(queryset, per_page, orphans, allow_empty_first_page)

    def setup(self):
        paginator = self.get_paginator(self.queryset, self.list_per_page)
        result_count = paginator.count
        # Determine use pagination.
        multi_page = result_count > self.list_per_page

        self.result_count = result_count
        self.multi_page = multi_page
        self.paginator = paginator
        self.page = paginator.get_page(self.page_num)

    def get_objects(self):
        if not self.multi_page:
            result_list = self.queryset._clone()
        else:
            try:
                result_list = self.paginator.page(self.page_num).object_list
            except InvalidPage:
                raise IncorectLookupParameter
        return result_list
