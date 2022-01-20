from django.db import migrations, models
import django.db.models.deletion
import huscy.project_ethics.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ethic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, default='', max_length=255, verbose_name='Code')),
            ],
            options={
                'verbose_name': 'Ethic',
                'verbose_name_plural': 'Ethics',
                'ordering': ('-project', 'ethic_board__name'),
            },
        ),
        migrations.CreateModel(
            name='EthicBoard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Ethic board',
                'verbose_name_plural': 'Ethic boards',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='EthicFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filetype', models.PositiveSmallIntegerField(choices=[(0, 'Ethic proposal'), (1, 'Ethic votum'), (2, 'Ethic amendment')], verbose_name='File type')),
                ('filehandle', models.FileField(upload_to=huscy.project_ethics.models.EthicFile.get_upload_path, verbose_name='File handle')),
                ('filename', models.CharField(max_length=255, verbose_name='File name')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Uploaded at')),
                ('uploaded_by', models.CharField(editable=False, max_length=126, verbose_name='Uploaded by')),
                ('ethic', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='ethic_files', to='project_ethics.ethic', verbose_name='Ethic')),
            ],
            options={
                'verbose_name': 'Ethic file',
                'verbose_name_plural': 'Ethic files',
                'ordering': ('-ethic__project', '-ethic', 'filename'),
            },
        ),
        migrations.AddField(
            model_name='ethic',
            name='ethic_board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='project_ethics.ethicboard', verbose_name='Ethic board'),
        ),
        migrations.AddField(
            model_name='ethic',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ethics', to='projects.project', verbose_name='Project'),
        ),
        migrations.AlterUniqueTogether(
            name='ethic',
            unique_together={('project', 'ethic_board')},
        ),
    ]
