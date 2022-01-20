import django.core.validators
from django.db import migrations, models
import huscy.project_ethics.models


class Migration(migrations.Migration):

    dependencies = [
        ('project_ethics', '0002_auto_20211101_0600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ethicfile',
            name='filehandle',
            field=models.FileField(max_length=255, upload_to=huscy.project_ethics.models.EthicFile.get_upload_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='File handle'),
        ),
    ]
