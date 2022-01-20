# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tests.test_main.test_main.settings')
from black_mirror import api
os.environ.setdefault('WIKIBASE_URL', api('wikibase').url)
os.environ.setdefault('SPARQL_ENDPOINT', api('sparql').url)

django.setup()

# End of section for predefined environment values


from django.test import TestCase

from tests.test_main.model_fields.models import BigS, UnicodeSlugField


class SlugFieldTests(TestCase):

    def test_slugfield_max_length(self):
        """
        SlugField honors max_length.
        """
        bs = BigS.objects.create(s='slug' * 50)
        bs = BigS.objects.get(pk=bs.pk)
        self.assertEqual(bs.s, 'slug' * 50)

    def test_slugfield_unicode_max_length(self):
        """
        SlugField with allow_unicode=True honors max_length.
        """
        bs = UnicodeSlugField.objects.create(s='你好你好' * 50)
        bs = UnicodeSlugField.objects.get(pk=bs.pk)
        self.assertEqual(bs.s, '你好你好' * 50)
