from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0004_auto_20200908_0853'),
    ]

    operations = [
        migrations.AddField(
            model_name='importsetup',
            name='state',
            field=models.PositiveIntegerField(
                choices=[
                    (1, 'None'), (2, 'Error'), (3, 'Populating'),
                    (4, 'Executing')
                ], default=1, help_text='The last recorded state of the '
                'import setup.', verbose_name='State'
            ),
        ),
    ]
