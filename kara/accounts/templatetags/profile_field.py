from django.template import Library

register = Library()


@register.inclusion_tag("accounts/forms/field.html")
def render_field(field, is_owner=False):
    return {
        "field": field,
        "is_owner": is_owner,
    }
