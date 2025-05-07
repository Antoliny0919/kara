from pathlib import Path

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def file_name(value):
    """
    Extract the file name from a path-like string.
    """
    return Path(value).name
