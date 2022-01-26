from ..base.type import type


def tmpl(template, target):
    the_type = type(target)
    if the_type == 'dict':
        return template.format(**target)

    if the_type == 'list':
        return template.format(*target)
