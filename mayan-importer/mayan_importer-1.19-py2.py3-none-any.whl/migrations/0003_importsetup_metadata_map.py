from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0002_auto_20200908_0458'),
    ]

    operations = [
        migrations.AddField(
            model_name='importsetup',
            name='metadata_map',
            field=models.TextField(
                blank=True, help_text='A YAML encoded dictionary to save '
                'the content of the item properties as metadata values. '
                'The dictionary must consist of an import item property '
                'key matched to a metadata type name.',
                verbose_name='Metadata map'
            ),
        ),
    ]
