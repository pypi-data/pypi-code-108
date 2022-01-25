from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0006_auto_20200924_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsetupitem',
            name='serialized_data',
            field=models.TextField(
                blank=True, default='{}', verbose_name='Serialized data'
            ),
        ),
    ]
