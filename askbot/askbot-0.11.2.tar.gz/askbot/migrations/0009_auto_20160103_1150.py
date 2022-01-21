# -*- coding: utf-8 -*-

from askbot.search.postgresql import setup_full_text_search
from django.db import models, migrations
import askbot
import os.path

def init_postgresql_fts(apps, schema_editor):
    conn = schema_editor.connection
    # if conn does not have an attribute vendor, there is probalby something
    # wrong with Django and we should raise an exception, i.e. provoke the
    # AttributeError
    if not hasattr(conn, 'vendor') or conn.vendor != 'postgresql':
        return

    script_path = os.path.join(
                        askbot.get_install_directory(),
                        'search',
                        'postgresql',
                        'thread_and_post_models_03012016.plsql'
                    )
    setup_full_text_search(script_path)

class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0008_auto_20160101_0951'),
    ]

    operations = [
            migrations.RunPython(init_postgresql_fts)
    ]

