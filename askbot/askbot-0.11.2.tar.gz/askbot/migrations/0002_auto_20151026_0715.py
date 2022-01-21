# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postrevision',
            name='email_address',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
