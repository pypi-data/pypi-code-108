from django import template
from django.utils.safestring import mark_safe

register = template.Library()


NONE = {
    None: '',
}

BOOLEAN = {
    True: '<i class="fas fa-check text-success"></i>',
    False: '<i class="fas fa-times text-danger"></i>',
}


@register.filter
def display(value):
    result = value
    if isinstance(value, (type(None), bool)):
        result = {
            **NONE,
            **BOOLEAN,
        }[value]
    return mark_safe(result)
