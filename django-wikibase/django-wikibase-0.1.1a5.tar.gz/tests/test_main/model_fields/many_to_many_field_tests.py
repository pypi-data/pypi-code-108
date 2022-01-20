# -*- coding: utf-8 -*-

from django.test.utils import isolate_apps
from django.test import SimpleTestCase
from django.db import models
from django.apps import apps
from black_mirror import api
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tests.test_main.test_main.settings')
os.environ.setdefault('WIKIBASE_URL', api('wikibase').url)
os.environ.setdefault('SPARQL_ENDPOINT', api('sparql').url)

django.setup()

# End of section for predefined environment values


class ManyToManyFieldTests(SimpleTestCase):

    @isolate_apps('tests.test_main.model_fields')
    def test_value_from_object_instance_without_pk(self):
        class ManyToManyModel(models.Model):
            m2m = models.ManyToManyField('self', models.CASCADE)

            class Meta:
                app_label = 'model_fields'

        instance = ManyToManyModel()
        qs = instance._meta.get_field('m2m').value_from_object(instance)
        self.assertEqual(qs.model, ManyToManyModel)
        self.assertEqual(list(qs), [])

    def test_abstract_model_pending_operations(self):
        """
        Many-to-many fields declared on abstract models should not add lazy
        relations to resolve relationship declared as string (#24215).
        """
        pending_ops_before = list(apps._pending_operations.items())

        class AbstractManyToManyModel(models.Model):
            fk = models.ForeignKey('missing.FK', models.CASCADE)

            class Meta:
                abstract = True

        self.assertIs(AbstractManyToManyModel._meta.apps, apps)
        self.assertEqual(
            pending_ops_before,
            list(apps._pending_operations.items()),
            'Pending lookup added for a many-to-many field on an abstract model'
        )

    @isolate_apps('tests.test_main.model_fields', 'tests.test_main.model_fields.many_to_many_field_tests')
    def test_abstract_model_app_relative_foreign_key(self):
        class AbstractReferent(models.Model):
            reference = models.ManyToManyField('Referred', through='Through')

            class Meta:
                app_label = 'model_fields'
                abstract = True

        def assert_app_model_resolved(label):
            class Referred(models.Model):
                class Meta:
                    app_label = label

            class Through(models.Model):
                referred = models.ForeignKey(
                    'Referred', on_delete=models.CASCADE)
                referent = models.ForeignKey(
                    'ConcreteReferent', on_delete=models.CASCADE)

                class Meta:
                    app_label = label

            class ConcreteReferent(AbstractReferent):
                class Meta:
                    app_label = label

            self.assertEqual(ConcreteReferent._meta.get_field(
                'reference').related_model, Referred)
            self.assertEqual(ConcreteReferent.reference.through, Through)

        assert_app_model_resolved('model_fields')
        assert_app_model_resolved('many_to_many_field_tests')
