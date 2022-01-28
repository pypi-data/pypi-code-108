# -*- coding: utf-8 -*-
"""
    tests.config.test_ConfigReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_expressions.mustache import MustacheTemplate


class TestConfigReader:
    def test_process_templates(self):
        config = "{{#if A}}{{B}}{{/if}}"
        params = {"A": "true", "B": "XYZ"}

        template = MustacheTemplate(config)
        result = template.evaluate_with_variables(params)

        assert "XYZ" == result
