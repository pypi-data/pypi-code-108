from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0010_remove_importsetup_metadata_map'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsetupitem',
            name='state',
            field=models.IntegerField(
                choices=[
                    (1, 'None'), (2, 'Error'), (3, 'Queued'),
                    (4, 'Complete'), (5, 'Complete')
                ], db_index=True, default=1, verbose_name='State'
            ),
        ),
    ]
