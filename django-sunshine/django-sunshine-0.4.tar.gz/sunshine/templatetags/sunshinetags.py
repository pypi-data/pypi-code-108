# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import json
from django import template
import humanize


register = template.Library()


@register.filter('jsonify')
def jsonify(value):
    return json.dumps(value, ensure_ascii=False)


@register.filter('naturalsize')
def naturalsize(value):
    return humanize.naturalsize(value)
