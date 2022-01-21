# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('askbot', '0012_rename_related_name_to_auth_user_from_Vote'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=64, choices=[(b'recv_feedback', b"Receive user's feedback email"), (b'recv_mod_alerts', b'Receive moderation alert emails'), (b'terminate_accounts', b'Terminate user accounts'), (b'download_user_data', b'Download user data')])),
                ('user', models.ForeignKey(related_name='askbot_roles', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'askbot_role',
            },
        ),
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name': 'activity', 'verbose_name_plural': 'activities'},
        ),
        migrations.AlterModelOptions(
            name='award',
            options={'verbose_name': 'award', 'verbose_name_plural': 'awards'},
        ),
        migrations.AlterModelOptions(
            name='badgedata',
            options={'ordering': ('display_order', 'slug'), 'verbose_name': 'badge data', 'verbose_name_plural': 'badge data'},
        ),
        migrations.AlterModelOptions(
            name='favoritequestion',
            options={'verbose_name': 'favorite question', 'verbose_name_plural': 'favorite questions'},
        ),
        migrations.AlterModelOptions(
            name='postflagreason',
            options={'verbose_name': 'post flag reason', 'verbose_name_plural': 'post flag reasons'},
        ),
        migrations.AlterModelOptions(
            name='postrevision',
            options={'ordering': ('-revision',), 'verbose_name': 'post revision', 'verbose_name_plural': 'post revisions'},
        ),
        migrations.AlterModelOptions(
            name='replyaddress',
            options={'verbose_name': 'reply address', 'verbose_name_plural': 'reply addresses'},
        ),
        migrations.AlterModelOptions(
            name='repute',
            options={'verbose_name': 'repute', 'verbose_name_plural': 'repute'},
        ),
        migrations.AlterModelOptions(
            name='threadtogroup',
            options={'verbose_name': 'thread to group', 'verbose_name_plural': 'threads to groups'},
        ),
        migrations.AlterModelOptions(
            name='vote',
            options={'verbose_name': 'vote', 'verbose_name_plural': 'votes'},
        ),
        migrations.AlterField(
            model_name='emailfeedsetting',
            name='frequency',
            field=models.CharField(default=b'n', max_length=8, choices=[(b'i', 'instantly'), (b'd', 'daily'), (b'w', 'weekly'), (b'n', 'never')]),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('user', 'role')]),
        ),
    ]
