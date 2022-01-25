from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='importsetup',
            options={
                'ordering': ('label',), 'verbose_name': 'Import setup',
                'verbose_name_plural': 'Import setups'
            },
        ),
        migrations.RemoveField(
            model_name='importsetup',
            name='filename_regex',
        ),
        migrations.RemoveField(
            model_name='importsetup',
            name='folder_regex',
        ),
        migrations.AddField(
            model_name='importsetup',
            name='backend_data',
            field=models.TextField(blank=True, verbose_name='Backend data'),
        ),
        migrations.AddField(
            model_name='importsetup',
            name='backend_path',
            field=models.CharField(
                default='', help_text='The dotted Python path to the '
                'backend class.', max_length=128, verbose_name='Backend path'
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='importsetup',
            name='label',
            field=models.CharField(
                help_text='Short description of this import setup.',
                max_length=128, unique=True, verbose_name='Label'
            ),
        ),
    ]
