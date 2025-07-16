from django.utils.translation import gettext_lazy as _
from django_components import Component, register
from pydantic import BaseModel


@register("button")
class LinkButton(Component):
    template_file = "templates/link_button.html"

    class Kwargs(BaseModel):
        text: str = ""
        link: str = ""
        extra_css: str = ""

    def get_template_data(self, args, kwargs, slots, context):
        return {
            "text": _(kwargs.text),
            "link": kwargs.link,
            "extra_css": kwargs.extra_css,
        }


@register("count_up_number")
class CountUpNumber(Component):
    template_file = "templates/count_up_number.html"

    class Kwargs(BaseModel):
        extra_css: str = ""
        initial: int = 0
        purpose: int = 0

    def get_template_data(self, args, kwargs, slots, context):
        return {
            "extra_css": kwargs.extra_css,
            "initial": kwargs.initial,
            "purpose": kwargs.purpose,
        }
