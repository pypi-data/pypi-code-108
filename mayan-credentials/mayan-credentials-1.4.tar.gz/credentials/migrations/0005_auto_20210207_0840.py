
import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):
    dependencies = [
        ('credentials', '0004_auto_20210207_0823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storedcredential',
            name='internal_name',
            field=models.CharField(db_index=True, help_text='This value will be used by other apps to reference this credential. Can only contain letters, numbers, and underscores.', max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[a-zA-Z0-9_]+\\Z'), "Enter a valid 'internal name' consisting of letters, numbers, and underscores.", 'invalid')], verbose_name='Internal name'),
        ),
    ]
