from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0005_importsetup_state'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importsetupitem',
            old_name='metadata',
            new_name='serialized_data',
        ),
    ]
