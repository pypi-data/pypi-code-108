from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_ethics', '0003_alter_ethicfile_filehandle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ethicfile',
            name='filetype',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Proposal'), (1, 'Attachment'), (2, 'Vote'), (3, 'Cover letter')], verbose_name='File type'),
        ),
    ]
