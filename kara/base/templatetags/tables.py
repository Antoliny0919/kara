from django import template
from django.conf import settings
from django.http import QueryDict
from django.template.defaulttags import querystring
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def pagination_number(pagination, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == pagination.paginator.ELLIPSIS:
        return format_html("{} ", pagination.paginator.ELLIPSIS)
    elif i == pagination.page_num:
        return format_html('<em class="current-page" aria-current="page">{}</em> ', i)
    else:
        link = querystring(
            context=None, query_dict=QueryDict(f"{settings.PAGE_VAR}={i}")
        )
        return format_html(
            '<a href="{}" hx-get="{}" aria-label="page {}" {}>{}</a> ',
            link,
            link,
            i,
            mark_safe(' class="end"' if i == pagination.paginator.num_pages else ""),
            i,
        )


@register.inclusion_tag("base/tables/pagination.html", name="pagination")
def pagination_tag(pagination, **kwargs):
    previous_page_num = pagination.page_num - 1
    next_page_num = pagination.page_num + 1
    previous_page_link = querystring(
        context=None, query_dict=QueryDict(f"{settings.PAGE_VAR}={previous_page_num}")
    )
    next_page_link = querystring(
        context=None, query_dict=QueryDict(f"{settings.PAGE_VAR}={next_page_num}")
    )
    return {
        "pagination": pagination,
        "previous_page_link": previous_page_link,
        "next_page_link": next_page_link,
        **kwargs,
    }
