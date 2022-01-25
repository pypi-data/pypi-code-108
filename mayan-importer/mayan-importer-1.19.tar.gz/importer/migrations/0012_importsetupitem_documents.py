from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0054_trasheddocument'),
        ('importer', '0011_auto_20201004_0042'),
    ]

    operations = [
        migrations.AddField(
            model_name='importsetupitem',
            name='documents',
            field=models.ManyToManyField(
                blank=True, related_name='import_items',
                to='documents.Document', verbose_name='Document'
            ),
        ),
    ]
