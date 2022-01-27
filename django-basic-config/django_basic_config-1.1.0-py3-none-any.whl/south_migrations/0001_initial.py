# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Config_Property'
        db.create_table(u'django_config_config_property', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('property_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('property_value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'django_config', ['Config_Property'])


    def backwards(self, orm):
        # Deleting model 'Config_Property'
        db.delete_table(u'django_config_config_property')


    models = {
        u'django_config.config_property': {
            'Meta': {'object_name': 'Config_Property'},
            'application': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'property_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'property_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['django_config']