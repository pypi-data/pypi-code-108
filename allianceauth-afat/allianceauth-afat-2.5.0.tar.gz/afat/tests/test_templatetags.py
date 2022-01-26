"""
Test our template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase

# Alliance Auth AFAT
from afat import __version__


class TestAfatFilters(TestCase):
    """
    Test template filters
    """

    def test_month_name_filter(self):
        """
        Test month_name
        :return:
        """

        context = Context({"month": 5})
        template_to_render = Template("{% load filters %} {{ month|month_name }}")

        rendered_template = template_to_render.render(context)

        self.assertInHTML("May", rendered_template)


class TestAfatVersionedStatic(TestCase):
    """
    Test versioned static template tag
    """

    def test_versioned_static(self):
        """
        Test afat_versioned_static
        :return:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            "{% load afat_versioned_static %}"
            "{% afat_static 'afat/css/allianceauth-afat.min.css' %}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            f'/static/afat/css/allianceauth-afat.min.css?v={context["version"]}',
            rendered_template,
        )
