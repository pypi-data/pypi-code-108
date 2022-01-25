from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0007_auto_20200924_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsetup',
            name='credential',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='import_setups',
                to='credentials.StoredCredential', verbose_name='Credential'
            ),
        ),
    ]
