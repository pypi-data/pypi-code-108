from django.db import migrations


def operation_rename_credential_modules(apps, schema_editor):
    StoredCredential = apps.get_model(
        app_label='credentials', model_name='StoredCredential'
    )

    for stored_credential in StoredCredential.objects.using(alias=schema_editor.connection.alias).all():
        parts = stored_credential.backend_path.split('.')
        parts[-2] = 'credential_backends'
        stored_credential.backend_path = '.'.join(parts)
        stored_credential.save()


def operation_rename_credential_modules_reverse(apps, schema_editor):
    StoredCredential = apps.get_model(
        app_label='credentials', model_name='StoredCredential'
    )

    for stored_credential in StoredCredential.objects.using(alias=schema_editor.connection.alias).all():
        parts = stored_credential.backend_path.split('.')
        parts[-2] = 'credentials'
        stored_credential.backend_path = '.'.join(parts)
        stored_credential.save()


class Migration(migrations.Migration):
    dependencies = [
        ('credentials', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            code=operation_rename_credential_modules,
            reverse_code=operation_rename_credential_modules_reverse
        ),
    ]
