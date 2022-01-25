from django.db import migrations, models

import mayan.apps.common.validators


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0003_importsetup_metadata_map'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsetup',
            name='metadata_map',
            field=models.TextField(
                blank=True, help_text='A YAML encoded dictionary to save '
                'the content of the item properties as metadata values. '
                'The dictionary must consist of an import item property '
                'key matched to a metadata type name.', validators=[
                    mayan.apps.common.validators.YAMLValidator()
                ], verbose_name='Metadata map'
            ),
        ),
    ]
