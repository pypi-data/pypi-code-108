# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_permission(app, schema):
    ContentType = app.get_model("contenttypes", "ContentType")
    Permission = app.get_model("auth", "Permission")
    content_type, created = ContentType.objects.get_or_create(
        app_label="modeltranslation_rosetta", model="trans"
    )

    Permission.objects.create(
        name="Can change Modeltranslation-rosetta",
        content_type=content_type,
        codename="change_trans",
    )


class Migration(migrations.Migration):
    dependencies = []

    operations = [migrations.RunPython(add_permission)]
