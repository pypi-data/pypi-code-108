# coding: utf-8
from __future__ import unicode_literals

from django.template import Library

register = Library()


@register.simple_tag(takes_context=True)
def get_params(context, field, value):
    dict_ = context["request"].GET.copy()
    dict_[field] = value
    return dict_.urlencode()
