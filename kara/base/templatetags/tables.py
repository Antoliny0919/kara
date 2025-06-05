from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .base_templatetags import querystring

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
        link = querystring(None, pagination.params, {settings.PAGE_VAR: i})
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
    return {
        "pagination": pagination,
        "previous_page": {settings.PAGE_VAR: previous_page_num},
        "next_page": {settings.PAGE_VAR: next_page_num},
        **kwargs,
    }


@register.inclusion_tag("base/tables/search_form.html", name="search_form")
def search_form_tag(table, **kwargs):
    return {
        "table": table,
        "field": table.search_form[settings.SEARCH_VAR],
        "model_name": table.opts.verbose_name,
        "clear_param": {settings.SEARCH_VAR: None},
        **kwargs,
    }


@register.simple_tag
def display_table_value(table, obj, column):
    """
    Returns the display value of a table row.
    This tag allows applying various formatting based on the field type.
    You can implement the detailed formatting logic in the
    `table.display_for_value` method.
    """
    return table.display_for_value(obj, column)
