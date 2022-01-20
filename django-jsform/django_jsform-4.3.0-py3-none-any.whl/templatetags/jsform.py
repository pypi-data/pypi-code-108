import json
import time

from django import forms, template
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

def get_errormessage_id(bound_field):
    return f'error-{bound_field.html_name}'
def _add_widget_attr(bound_field, name, value):
    _as_widget = bound_field.as_widget
    def as_widget(widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        attrs[name] = value
        return _as_widget(widget=widget, attrs=attrs, only_initial=only_initial)
    bound_field.as_widget = as_widget

@register.filter
def is_single_checkbox(bound_field):
    return isinstance(bound_field.field, forms.BooleanField)

@register.filter
def with_error_message_container(bound_field):
    return format_html('''
        {field}
        {error_message_container}
    ''', field=with_error_attributes(bound_field), error_message_container=error_message_container(bound_field))

@register.filter
def with_error_attributes(bound_field):
    '''
        Can be used (in conjunction with error_message_container) when with_error_message_container is not flexible enough.

        See how form_fields.html uses this to render checkboxes.
    '''
    error_message_id = get_errormessage_id(bound_field)
    bound_field._error_message_id = error_message_id
    _add_widget_attr(bound_field, 'aria-errormessage', error_message_id)
    if bound_field.errors :
        _add_widget_attr(bound_field, 'aria-invalid', 'true')
    return bound_field
@register.filter
def error_message_container(bound_field):
    '''
        Important: we always generate the error message container, even if empty.

        This is important, because aria-live only works for elements that are initially in the DOM.

        It also makes it easier to add error messages later via js (see how js_response.set_form_errors() works).

        Lastly, jsform_elementmerge.js doesn't work as desired if you have "optional" elements with any subsequent siblings, so it's always best to put them in their own container.
    '''
    try :
        error_message_id = bound_field._error_message_id
    except AttributeError :
        raise Exception('You must call "with_error_attributes(bound_field)" on the bound field before you call this function (or the field won\'t be rendered with the correct attributes to link it to this error message container')
    return format_html('''\
        <div class="error" aria-live="polite" id="{error_message_id}">{errors}</div>
    ''', error_message_id=error_message_id, errors='. '.join(bound_field.errors))

@register.filter
def with_widget_attr(bound_field, attr):
    # Note - this MUTATES the bound_field
    # You can call this as many times as you like, with different attributes
    # Can be used sort of like django-widget-tweaks to add arbitrary widget attributes from the template
    name, value = attr.split(',', 1)
    _add_widget_attr(bound_field, name, value)
    return bound_field