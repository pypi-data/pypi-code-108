from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('documents', '0054_trasheddocument'),
        ('credentials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportSetup',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'label', models.CharField(
                        help_text='Short description of this import setup.',
                        max_length=128, verbose_name='Label'
                    )
                ),
                (
                    'folder_regex', models.CharField(
                        blank=True, max_length=128, null=True,
                        verbose_name='Folder regular expression'
                    )
                ),
                (
                    'filename_regex', models.CharField(
                        blank=True, max_length=128, null=True,
                        verbose_name='Filename regular expression'
                    )
                ),
                (
                    'process_size', models.PositiveIntegerField(
                        default=2, help_text='Number of items to process '
                        'per execution.', verbose_name='Process size.'
                    )
                ),
                (
                    'credential', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='import_setups',
                        to='credentials.StoredCredential',
                        verbose_name='Credential'
                    )
                ),
                (
                    'document_type', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='import_setups',
                        to='documents.DocumentType',
                        verbose_name='Document type'
                    )
                ),
            ],
            options={
                'verbose_name': 'Import setup',
                'verbose_name_plural': 'Import setups',
            },
        ),
        migrations.CreateModel(
            name='ImportSetupItem',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'identifier', models.CharField(
                        db_index=True, max_length=64,
                        verbose_name='Identifier'
                    )
                ),
                (
                    'metadata', models.TextField(
                        blank=True, verbose_name='Metadata'
                    )
                ),
                (
                    'state', models.IntegerField(
                        choices=[
                            (1, 'None'), (2, 'Error'), (3, 'Queued'),
                            (4, 'Complete'), (5, 'Complete')
                        ], default=1, verbose_name='State'
                    )
                ),
                (
                    'state_data', models.TextField(
                        blank=True, verbose_name='State data'
                    )
                ),
                (
                    'import_setup', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='items', to='importer.ImportSetup',
                        verbose_name='Import setup'
                    )
                ),
            ],
            options={
                'verbose_name': 'Import setup item',
                'verbose_name_plural': 'Import setup items',
            },
        ),
    ]
