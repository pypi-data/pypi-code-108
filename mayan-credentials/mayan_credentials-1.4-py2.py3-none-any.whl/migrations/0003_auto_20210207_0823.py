import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):
    dependencies = [
        ('credentials', '0002_auto_20201215_0523'),
    ]

    operations = [
        migrations.AddField(
            model_name='storedcredential',
            name='internal_name',
            field=models.CharField(blank=True, db_index=True, help_text='This value will be used by other apps to reference this credential. Can only contain letters, numbers, and underscores.', max_length=255, null=True, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[a-zA-Z0-9_]+\\Z'), "Enter a valid 'internal name' consisting of letters, numbers, and underscores.", 'invalid')], verbose_name='Internal name'),
        ),
        migrations.AlterField(
            model_name='storedcredential',
            name='backend_data',
            field=models.TextField(blank=True, help_text='JSON encoded data for the backend class.', verbose_name='Backend data'),
        ),
    ]
