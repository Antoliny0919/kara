from django.template import Library
from django.utils.translation import gettext_lazy as _

register = Library()


@register.inclusion_tag(
    "wedding_gifts/components/footer_navigation.html", name="footer_navigation"
)
def footer_navigation(left_title, right_title, previous_page_link, next_page_link):
    print(previous_page_link, "suuuuuuu")
    return {
        "left_title": _(left_title),
        "right_title": _(right_title),
        "previous_page_link": previous_page_link,
        "next_page_link": next_page_link,
    }
