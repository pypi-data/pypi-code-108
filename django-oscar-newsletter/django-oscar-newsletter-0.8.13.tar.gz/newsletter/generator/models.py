import logging
from django.db import models
from django.utils.translation import ugettext as _
from django.template.loader import get_template
from django.template import Template

logger = logging.getLogger(__name__)


def default_html():
    path = get_template(
        'newsletter/message/default_footer.html'
    ).origin.name
    with open(path, 'r', encoding='UTF-8') as file:
        return file.read()

def default_text():
    path = get_template(
        'newsletter/message/default_footer.txt'
    ).origin.name
    with open(path, 'r', encoding='UTF-8') as file:
        return file.read()


class NewsletterMixin(models.Model):

    footer_template_html = models.TextField(
        _('Footer Template (HTML)'),
        default=default_html,
        blank=True, null=True,
    )
    footer_template_text = models.TextField(
        _('Footer Template (Text)'),
        default=default_text,
        blank=True, null=True,
    )

    @property
    def footer_html(self):
        return Template(self.footer_template_html)

    @property
    def footer_text(self):
        return Template(self.footer_template_text)

    class Meta:
        abstract = True
