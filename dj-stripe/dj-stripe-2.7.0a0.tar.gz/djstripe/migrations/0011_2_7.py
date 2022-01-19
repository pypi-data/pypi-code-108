# Generated by Django 3.2.11 on 2022-01-19 04:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations

import djstripe.fields


class Migration(migrations.Migration):

    dependencies = [
        ("djstripe", "0010_alter_customer_balance"),
    ]

    operations = [
        migrations.AddField(
            model_name="webhookeventtrigger",
            name="webhook_endpoint",
            field=djstripe.fields.StripeForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="djstripe.webhookendpoint",
                to_field=settings.DJSTRIPE_FOREIGN_KEY_TO_FIELD,
            ),
        ),
    ]
