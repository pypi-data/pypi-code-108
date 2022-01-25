from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('importer', '0008_auto_20200924_0903'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportSetupAction',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'backend_path', models.CharField(
                        help_text='The dotted Python path to the backend '
                        'class.', max_length=128, verbose_name='Backend path'
                    )
                ),
                (
                    'backend_data', models.TextField(
                        blank=True, verbose_name='Backend data'
                    )
                ),
                (
                    'label', models.CharField(
                        help_text='A short text describing the action.',
                        max_length=255, verbose_name='Label'
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, verbose_name='Enabled'
                    )
                ),
                (
                    'order', models.PositiveIntegerField(
                        blank=True, db_index=True, default=0,
                        help_text='Order in which the action will be '
                        'executed. If left unchanged, an automatic order '
                        'value will be assigned.', verbose_name='Order'
                    )
                ),
                (
                    'import_setup', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='actions', to='importer.ImportSetup',
                        verbose_name='Import Setup'
                    )
                ),
            ],
            options={
                'verbose_name': 'Import setup action',
                'verbose_name_plural': 'Import setup actions',
                'ordering': ('order', 'label'),
                'unique_together': {
                    ('import_setup', 'label'), ('import_setup', 'order')
                },
            },
        ),
    ]
