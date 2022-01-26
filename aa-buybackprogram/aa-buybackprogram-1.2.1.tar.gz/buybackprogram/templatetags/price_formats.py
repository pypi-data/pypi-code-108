from django import template

register = template.Library()


@register.filter
def price(value):
    if value:
        return value + " ISK"
    else:
        return "-"


@register.filter
def tax(value):
    if value:
        return str(value) + " %"
    else:
        return "-"
