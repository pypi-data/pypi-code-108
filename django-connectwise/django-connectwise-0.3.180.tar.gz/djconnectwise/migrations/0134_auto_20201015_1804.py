# Generated by Django 3.1.2 on 2020-10-15 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djconnectwise', '0133_activityudftracker_opportunityudftracker_projectudftracker_ticketudftracker'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activityudf',
            old_name='entryMethod',
            new_name='entry_method',
        ),
        migrations.RenameField(
            model_name='activityudf',
            old_name='numberOfDecimals',
            new_name='number_of_decimals',
        ),
        migrations.RenameField(
            model_name='opportunityudf',
            old_name='entryMethod',
            new_name='entry_method',
        ),
        migrations.RenameField(
            model_name='opportunityudf',
            old_name='numberOfDecimals',
            new_name='number_of_decimals',
        ),
        migrations.RenameField(
            model_name='projectudf',
            old_name='entryMethod',
            new_name='entry_method',
        ),
        migrations.RenameField(
            model_name='projectudf',
            old_name='numberOfDecimals',
            new_name='number_of_decimals',
        ),
        migrations.RenameField(
            model_name='ticketudf',
            old_name='entryMethod',
            new_name='entry_method',
        ),
        migrations.RenameField(
            model_name='ticketudf',
            old_name='numberOfDecimals',
            new_name='number_of_decimals',
        ),
    ]
