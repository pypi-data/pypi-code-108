import django.core.validators
from django.db import migrations, models
import huscy.project_ethics.models


class Migration(migrations.Migration):

    dependencies = [
        ('project_ethics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ethic',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='ethicboard',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='ethicfile',
            name='filehandle',
            field=models.FileField(upload_to=huscy.project_ethics.models.EthicFile.get_upload_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='File handle'),
        ),
        migrations.AlterField(
            model_name='ethicfile',
            name='filetype',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Proposal'), (1, 'Attachment'), (2, 'Vote')], verbose_name='File type'),
        ),
        migrations.AlterField(
            model_name='ethicfile',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
