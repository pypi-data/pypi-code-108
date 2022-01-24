from django import template

from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def add_class_to_el(value: str, arg: str) -> str:
    """Add a CSS class to every occurence of an element type.

    :Example:

    .. code-block::

        {{ mymodel.myhtmlfield|add_class_to_el:"ul,browser-default" }}
    """
    el, cls = arg.split(",")
    soup = BeautifulSoup(value, "html.parser")

    for el in soup.find_all(el):
        el["class"] = el.get("class", []) + [cls]

    return str(soup)
