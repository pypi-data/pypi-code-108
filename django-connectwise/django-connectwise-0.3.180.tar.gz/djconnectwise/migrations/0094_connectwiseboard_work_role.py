# Generated by Django 2.1 on 2019-07-16 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djconnectwise', '0093_merge_20190716_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectwiseboard',
            name='work_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djconnectwise.WorkRole'),
        ),
    ]
