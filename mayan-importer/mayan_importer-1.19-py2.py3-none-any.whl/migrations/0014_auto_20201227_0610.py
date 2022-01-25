from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0013_auto_20201225_0155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsetuplog',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Date time'),
        ),
    ]
