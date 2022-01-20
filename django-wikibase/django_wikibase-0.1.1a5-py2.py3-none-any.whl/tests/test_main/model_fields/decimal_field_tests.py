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

from decimal import Decimal
from unittest import skipUnless

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from tests.test_main.model_fields.models import BigD, Foo


class DecimalFieldTests(TestCase):

    def test_to_python(self):
        f = models.DecimalField(max_digits=4, decimal_places=2)
        self.assertEqual(f.to_python(3), Decimal('3'))
        self.assertEqual(f.to_python('3.14'), Decimal('3.14'))
        with self.assertRaises(ValidationError):
            f.to_python('abc')

    def test_default(self):
        f = models.DecimalField(default=Decimal('0.00'))
        self.assertEqual(f.get_default(), Decimal('0.00'))

    @skipUnless(False, "DecimalField hasn't _format() method")
    def test_format(self):
        f = models.DecimalField(max_digits=5, decimal_places=1)
        self.assertEqual(f._format(f.to_python(2)), '2.0')
        self.assertEqual(f._format(f.to_python('2.6')), '2.6')
        self.assertIsNone(f._format(None))

    def test_get_prep_value(self):
        f = models.DecimalField(max_digits=5, decimal_places=1)
        self.assertIsNone(f.get_prep_value(None))
        self.assertEqual(f.get_prep_value('2.4'), Decimal('2.4'))

    def test_filter_with_strings(self):
        """
        Should be able to filter decimal fields using strings (#8023).
        """
        foo = Foo.objects.create(a='abc', d=Decimal('12.34'))
        self.assertEqual(list(Foo.objects.filter(d='12.34')), [foo])

    def test_save_without_float_conversion(self):
        """
        Ensure decimals don't go through a corrupting float conversion during
        save (#5079).
        """
        bd = BigD(d='12.9')
        bd.save()
        bd = BigD.objects.get(pk=bd.pk)
        self.assertEqual(bd.d, Decimal('12.9'))

    def test_lookup_really_big_value(self):
        """
        Really big values can be used in a filter statement.
        """
        # This should not crash.
        Foo.objects.filter(d__gte=100000000000)

    def test_max_digits_validation(self):
        field = models.DecimalField(max_digits=2)
        expected_message = validators.DecimalValidator.messages['max_digits'] % {'max': 2}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(100, None)

    def test_max_decimal_places_validation(self):
        field = models.DecimalField(decimal_places=1)
        expected_message = validators.DecimalValidator.messages['max_decimal_places'] % {'max': 1}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal('0.99'), None)

    def test_max_whole_digits_validation(self):
        field = models.DecimalField(max_digits=3, decimal_places=1)
        expected_message = validators.DecimalValidator.messages['max_whole_digits'] % {'max': 2}
        with self.assertRaisesMessage(ValidationError, expected_message):
            field.clean(Decimal('999'), None)
