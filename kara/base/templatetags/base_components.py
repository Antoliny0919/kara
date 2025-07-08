from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.inclusion_tag("base/components/section_header.html", name="section_header")
def section_header_tag(image, title, subtitle):
    return {
        "image_path": image,
        "title": _(title),
        "subtitle": _(subtitle),
    }


@register.inclusion_tag("base/components/count_up_number.html")
def count_up_number(purpose, extra_css=""):
    return {
        "purpose": purpose,
        "extra_css": extra_css,
    }
