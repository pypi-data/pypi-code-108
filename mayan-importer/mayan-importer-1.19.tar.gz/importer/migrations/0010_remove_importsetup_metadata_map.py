from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0009_importsetupaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='importsetup',
            name='metadata_map',
        ),
    ]
