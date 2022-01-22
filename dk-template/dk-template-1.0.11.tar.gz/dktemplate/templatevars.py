# -*- coding: utf-8 -*-
"""Parse a django template and find all template variables that are used.
   Output the template variables in a format that can be included in the
   template to verify the values of all context variables.
"""
from __future__ import print_function

import re
import sys

from dktemplate.parse import nest
from dktemplate.tokenize import tokenize


def templatevars(t):
    """Will return the template variables...
    """
    tag_and_vals = []
    txt = re.sub(r'{#.*?#}', '', t)
    tag_and_vals += re.findall(r'{(?:%|{).*?(?:}|%)}', txt)
    return nest(tag_and_vals)


def main(fname=None):
    """cli entry point.
    """
    template = open(fname or sys.argv[1]).read()
    template = re.sub(r'TEMPLATEVARS:.*?:TEMPLATEVARS', "", template)
    txt = repr(nest(tokenize(template), fname))
    txt = txt.replace('{% end-program %}', '</pre>:TEMPLATEVARS' + '<br>' * 5)
    txt = txt.replace('{% -program None %} ==> []', '')
    # txt = re.sub(r'{%\s*load.*?%}', '', txt)
    txt = 'TEMPLATEVARS:<pre>' + txt
    print(txt)
    # pprint.pprint()
    # print render(template)
    return txt


if __name__ == "__main__":
    main()
