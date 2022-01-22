# -*- coding: utf-8 -*-

from django import template

from dktemplate.find_template import find_template
from dktemplate.parse import parse_file

register = template.Library()


@register.inclusion_tag('dktemplate/freevars.html', takes_context=True)
def freevars(context):
    template_fname = context['dbg_template_name']
    try:
        tmpl_path = find_template(template_fname)
        ast = parse_file(tmpl_path)
        _fvars = ast.fvars()
        contextvars = set()
        for d in context.dicts:
            contextvars |= set(d.keys())

        common_page_vars = set("""
        path full_path funky_path session method COOKIES LANGUAGE_CODE DEBUG
        is_post is_get request adminip page_secret_selfref uuid
        False None True csrfcookie dbg_template_name dbg_view_name
        dkhttp_integration
        """.split())
        overflow = list(contextvars - _fvars - common_page_vars)
        overflow.sort()
        fvars = [dict(name=fv, value=context.get(fv, u"[MISSING]")) for fv in _fvars]
        fvars.sort(key=lambda item: (str(item['value']) != '[MISSING]', item['name']))
        return {
            'fvars': fvars,
            'overflow': overflow,
        }
    except IOError:
        return {
            'fvars': [{'name': 'NOTHING', 'value': 'FOUND'}]
        }
