# -*- coding: utf-8 -*-
from pip_services3_expressions.mustache.MustacheTemplate import MustacheTemplate


class TestMustacheTemplate:

    def test_template_1(self):
        template = MustacheTemplate()
        template.template = "Hello, {{{NAME}}}{{ #if ESCLAMATION }}!{{/if}}{{{^ESCLAMATION}}}.{{{/ESCLAMATION}}}"
        variables = {
            'NAME': 'Alex',
            'ESCLAMATION': '1'
        }

        result = template.evaluate_with_variables(variables)
        assert "Hello, Alex!" == result

        template.default_variables['name'] = 'Mike'
        template.default_variables['esclamation'] = False

        result = template.evaluate()
        assert "Hello, Mike." == result
