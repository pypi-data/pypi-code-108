# Generated by Django 2.0.8 on 2019-02-12 14:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tellme', '0003_feedback_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation date'),
        ),
        migrations.AlterModelOptions(
            name='feedback',
            options={'verbose_name': 'feedback', 'verbose_name_plural': 'feedbacks'},
        ),
        migrations.AddField(
            model_name='feedback',
            name='ack',
            field=models.BooleanField(default=False, verbose_name='Acknowledgement'),
        ),
    ]
