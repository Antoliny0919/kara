from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .base_templatetags import querystring

register = template.Library()


@register.simple_tag
def pagination_number(pagination, i, htmx):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == pagination.paginator.ELLIPSIS:
        return format_html("{} ", pagination.paginator.ELLIPSIS)
    elif i == pagination.page_num:
        return format_html('<em class="current-page" aria-current="page">{}</em> ', i)
    else:
        link = querystring(None, pagination.params, {settings.PAGE_VAR: i})
        link_key = "href" if htmx is None else "hx-get"
        return format_html(
            '<a {}="{}" aria-label="page {}" {}>{}</a> ',
            link_key,
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


def table_headers(table):
    """
    Generates table headers by defining properties for each field
    """
    sorted_fields = {
        param.removeprefix("-"): param
        for param in table.params.get(settings.ORDER_VAR, [])
    }
    for field_name in table.columns:
        is_sortable = field_name in table.ordering
        verbose_name = table.opts.get_field(field_name).verbose_name
        # Sorting is not supported for this field
        if not is_sortable:
            yield {
                "text": verbose_name,
                "sortable": is_sortable,
                "class_attr": format_html(' class="column-{}"', field_name),
            }
            continue
        is_sorted = field_name in sorted_fields
        th_classes = format_html(
            ' class="{} column-{}"', "sorted" if is_sorted else "sortable", field_name
        )
        if is_sorted:
            # Sortable field and it is already sorted
            value = sorted_fields[field_name]
            order_type = "descending" if value.startswith("-") else "ascending"
            new_order_type = {"ascending": "descending", "descending": "ascending"}[
                order_type
            ]
            remove_sort_params = {
                key: value for key, value in sorted_fields.items() if key != field_name
            }
            reverse_direction = (
                f"-{field_name}" if new_order_type == "descending" else field_name
            )
            reverse_sort_params = sorted_fields.copy()
            reverse_sort_params[field_name] = reverse_direction
            yield {
                "text": verbose_name,
                "sortable": is_sortable,
                "sorted": True,
                "order_type": new_order_type,
                "remove_sort": {
                    settings.ORDER_VAR: [
                        value for _, value in remove_sort_params.items()
                    ]
                },
                "reverse_sort": {
                    settings.ORDER_VAR: [
                        value for _, value in reverse_sort_params.items()
                    ]
                },
                "class_attr": th_classes,
            }
            continue
        # Sortable field and it is not sorted yet.
        # First sorting is applied in ascending order.
        sort_params = sorted_fields.copy()
        sort_params[field_name] = field_name
        yield {
            "text": verbose_name,
            "sortable": is_sortable,
            "sorted": False,
            "order_type": "ascending",
            "sort": {settings.ORDER_VAR: [value for _, value in sort_params.items()]},
            "class_attr": th_classes,
        }


@register.inclusion_tag("base/tables/table.html", name="table")
def render_table(table, **kwargs):
    return {
        "table_headers": table_headers(table),
        "table": table,
        **kwargs,
    }
