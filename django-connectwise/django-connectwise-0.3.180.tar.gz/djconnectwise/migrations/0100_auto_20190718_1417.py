# Generated by Django 2.1 on 2019-07-18 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djconnectwise', '0099_timeentry_agreement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeentry',
            name='agreement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djconnectwise.Agreement'),
        ),
    ]
