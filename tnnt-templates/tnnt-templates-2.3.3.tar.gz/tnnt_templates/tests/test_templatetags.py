# Django
from django.template import Context, Template
from django.test import TestCase

# AA Templates: Terra Nanotech
from tnnt_templates import __version__


class TestTnntTemplateVariables(TestCase):
    """
    Test TN-NT Template tags
    """

    def test_startswith(self):
        """
        Test startswith
        :return:
        :rtype:
        """

        context = Context(
            {"content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."}
        )
        template_to_render = Template(
            "{% load tnnt_template_tags %}"
            '{% if content|startswith:"Lorem" %}{{ content }}{% endif %}'
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            rendered_template,
        )

    def test_tnnt_static(self):
        """
        Test tnnt_static
        :return:
        :rtype:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            "{% load tnnt_template_tags %}"
            "{% tnnt_static 'tnnt_templates/css/fonts.min.css' %}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            f'/static/tnnt_templates/css/fonts.min.css?v={context["version"]}',
            rendered_template,
        )
