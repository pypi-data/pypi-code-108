from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def navactive_2(request, url_name: str, *args):
    """returns the active class name for navs"""
    url = reverse(url_name, args=args)
    if request.path == url:
        return "active"
    else:
        return ""
