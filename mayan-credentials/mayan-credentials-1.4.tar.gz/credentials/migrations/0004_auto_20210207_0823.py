from django.db import migrations
from django.utils.text import slugify


def code_slugify_internal_name(apps, schema_editor):
    StoredCredential = apps.get_model(
        app_label='credentials', model_name='StoredCredential'
    )

    for stored_credential in StoredCredential.objects.using(alias=schema_editor.connection.alias).all():
        stored_credential.internal_name = slugify(value=stored_credential.label)
        stored_credential.save()


class Migration(migrations.Migration):
    dependencies = [
        ('credentials', '0003_auto_20210207_0823'),
    ]

    operations = [
        migrations.RunPython(
            code=code_slugify_internal_name,
            reverse_code=migrations.RunPython.noop
        ),
    ]
