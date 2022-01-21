# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LastVisitTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_type', models.SmallIntegerField(default=0, choices=[(0, b'email-like message, stored in the inbox'), (2, b'will be shown just once'), (1, b'will be shown until certain time')])),
                ('senders_info', models.TextField(default=b'')),
                ('headline', models.CharField(max_length=80)),
                ('text', models.TextField(help_text=b'source text for the message, e.g. in markdown format', null=True, blank=True)),
                ('html', models.TextField(help_text=b'rendered html of the message', null=True, blank=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('last_active_at', models.DateTimeField(auto_now_add=True)),
                ('active_until', models.DateTimeField(null=True, blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='group_messaging.Message', null=True, on_delete=models.CASCADE)),
                ('recipients', models.ManyToManyField(to='auth.Group')),
                ('root', models.ForeignKey(related_name='descendants', blank=True, to='group_messaging.Message', null=True, on_delete=models.CASCADE)),
                ('sender', models.ForeignKey(related_name='group_messaging_sent_messages', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageMemo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'seen'), (1, b'archived'), (2, b'deleted')])),
                ('message', models.ForeignKey(related_name='memos', to='group_messaging.Message', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SenderList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient', models.ForeignKey(to='auth.Group', unique=True, on_delete=models.CASCADE)),
                ('senders', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnreadInboxCounter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='messagememo',
            unique_together=set([('user', 'message')]),
        ),
        migrations.AddField(
            model_name='lastvisittime',
            name='message',
            field=models.ForeignKey(to='group_messaging.Message', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lastvisittime',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='lastvisittime',
            unique_together=set([('user', 'message')]),
        ),
    ]
