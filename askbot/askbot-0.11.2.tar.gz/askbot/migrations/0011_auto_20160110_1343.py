# -*- coding: utf-8 -*-


from django.db import models, migrations
import askbot.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0010_populate_language_code_for_reps_20160108_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localizeduserprofile',
            name='is_claimed',
            field=models.BooleanField(default=False, help_text=b'True, if user selects this language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='localizeduserprofile',
            name='language_code',
            field=askbot.models.fields.LanguageCodeField(default=b'en', max_length=16, db_index=True, choices=[(b'en', b'English'), (b'de', b'Deutsch')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='localizeduserprofile',
            name='reputation',
            field=models.PositiveIntegerField(default=0, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='primary_language',
            field=models.CharField(default=b'en', max_length=16, choices=[(b'en', b'English'), (b'de', b'Deutsch')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='reputation',
            field=models.PositiveIntegerField(default=1, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='status',
            field=models.CharField(default=b'w', max_length=2, db_index=True, choices=[(b'd', 'administrator'), (b'm', 'moderator'), (b'a', 'approved'), (b'w', 'watched'), (b's', 'suspended'), (b'b', 'blocked')]),
            preserve_default=True,
        ),
    ]
