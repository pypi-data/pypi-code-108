# -*- coding: utf-8 -*-
from os import path


def get_template_path(template_name):
    template_path = path.join(path.dirname(__file__), 'templates', template_name)
    if path.isfile(template_path):
        return template_path
    raise IOError('No such file %s', template_name)
