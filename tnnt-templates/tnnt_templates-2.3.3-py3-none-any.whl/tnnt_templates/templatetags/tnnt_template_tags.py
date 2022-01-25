"""
Template filter for Terra Nanotech templates
"""

# Django
from django.template.defaulttags import register
from django.templatetags.static import static

# AA Templates: Terra Nanotech
from tnnt_templates import __version__


@register.filter
def startswith(value, arg):
    """
    Usage, {% if value|starts_with:"arg" %}
    """

    return value.startswith(arg)


@register.simple_tag
def tnnt_static(path: str) -> str:
    """
    Versioned static URL
    :param path:
    :type path:
    :return:
    :rtype:
    """

    static_url = static(path)
    versioned_url = static_url + "?v=" + __version__

    return versioned_url
