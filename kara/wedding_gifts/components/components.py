from django.utils.translation import gettext_lazy as _
from django_components import Component, register
from pydantic import BaseModel


@register("header")
class Header(Component):
    template_file = "templates/header.html"

    class Kwargs(BaseModel):
        title: str
        image_path: str
        animate: bool = True
        detail_animate: str = "fade-in-down"
        subtitle: str = ""

    def get_template_data(self, args, kwargs, slots, context):
        return {
            "title": _(kwargs.title),
            "image_path": kwargs.image_path,
            "animate": kwargs.animate,
            "detail_animate": kwargs.detail_animate,
            "subtitle": _(kwargs.subtitle),
        }


@register("dashboard_section")
class DashboardSection(Component):
    template_file = "templates/dashboard_section.html"

    class Kwargs(BaseModel):
        header_title: str = ""
        header_title_description: str = ""
        header_layout_extra_css: str = ""

    def get_template_data(self, args, kwargs, slots, context):
        return {
            "header_title": _(kwargs.header_title),
            "header_title_description": _(kwargs.header_title_description),
            "header_layout_extra_css": kwargs.header_layout_extra_css,
        }


@register("insight_display_circle")
class InsightDisplayCircle(Component):
    template_file = "templates/insight_display_circle.html"

    class Kwargs(BaseModel):
        symbol_image: str
        title: str
        color: str = "kara-strong"

    def get_template_data(self, args, kwargs, slots, context):
        return {
            "symbol_image": kwargs.symbol_image,
            "title": _(kwargs.title),
            "color": kwargs.color,
        }


@register("insight_display_box")
class InsightDisplayBox(Component):
    template_file = "templates/insight_display_box.html"

    class Kwargs(BaseModel):
        symbol_image: str
        title: str
        color: str = "kara-strong"

    def get_template_data(self, args, kwargs, slots, context):
        return {
            "symbol_image": kwargs.symbol_image,
            "title": _(kwargs.title),
            "color": kwargs.color,
        }


@register("result_line")
class ResultLine(Component):
    template_file = "templates/result_line.html"

    class Kwargs(BaseModel):
        line_color: str = "kara-strong"

    def get_template_data(self, args, kwargs, slots, context):
        return {
            "line_color": kwargs.line_color,
        }
