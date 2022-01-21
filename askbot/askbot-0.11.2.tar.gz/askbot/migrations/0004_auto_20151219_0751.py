# -*- coding: utf-8 -*-


from askbot.search.postgresql import setup_full_text_search
from django.db import models, migrations
import askbot
import os.path

def init_postgresql_fts(apps, schema_editor):
    """This migration is no longer needed,
    as 0007 and 0009 have better FTS setup"""
    return

class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0003_auto_20151218_0909'),
    ]

    operations = [
        migrations.RunPython(init_postgresql_fts)
    ]
