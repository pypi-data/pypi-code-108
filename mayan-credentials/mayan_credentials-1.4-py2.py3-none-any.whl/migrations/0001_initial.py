from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='StoredCredential',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'label', models.CharField(
                        help_text='Short description of this credential.',
                        max_length=128, unique=True, verbose_name='Label'
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
            ],
            options={
                'verbose_name': 'Credential',
                'verbose_name_plural': 'Credentials',
                'ordering': ('label',),
            },
        ),
    ]
