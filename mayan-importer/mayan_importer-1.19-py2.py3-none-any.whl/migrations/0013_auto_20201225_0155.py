from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0012_importsetupitem_documents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsetup',
            name='backend_data',
            field=models.TextField(blank=True, help_text='JSON encoded data for the backend class.', verbose_name='Backend data'),
        ),
        migrations.AlterField(
            model_name='importsetup',
            name='process_size',
            field=models.PositiveIntegerField(default=2, help_text='Number of items to process per execution.', verbose_name='Process size'),
        ),
        migrations.AlterField(
            model_name='importsetupaction',
            name='backend_data',
            field=models.TextField(blank=True, help_text='JSON encoded data for the backend class.', verbose_name='Backend data'),
        ),
        migrations.CreateModel(
            name='ImportSetupLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='Date time')),
                ('text', models.TextField(blank=True, editable=False, verbose_name='Text')),
                ('import_setup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='importer.ImportSetup', verbose_name='Import setup log')),
            ],
            options={
                'verbose_name': 'Log entry',
                'verbose_name_plural': 'Log entries',
                'ordering': ('-datetime',),
                'get_latest_by': 'datetime',
            },
        ),
    ]
