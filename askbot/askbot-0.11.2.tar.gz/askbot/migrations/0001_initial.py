# -*- coding: utf-8 -*-


from django.db import models, migrations
import django_countries.fields
import picklefield.fields
import jsonfield.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity_type', models.SmallIntegerField(db_index=True, choices=[(1, 'asked a question'), (2, 'answered a question'), (3, 'commented question'), (4, 'commented answer'), (5, 'edited question'), (6, 'edited answer'), (7, 'received badge'), (8, 'marked best answer'), (9, 'upvoted'), (10, 'downvoted'), (11, 'canceled vote'), (12, 'deleted question'), (13, 'deleted answer'), (14, 'marked offensive'), (15, 'updated tags'), (16, 'selected favorite'), (17, 'completed user profile'), (18, 'email update sent to user'), (29, 'a post was shared'), (20, 'reminder about unanswered questions sent'), (21, 'reminder about accepting the best answer sent'), (19, 'mentioned in the post'), (22, 'created tag description'), (23, 'updated tag description'), (24, 'made a new post'), (25, 'made an edit'), (26, 'created post reject reason'), (27, 'updated post reject reason'), (28, b'sent email address validation message'), (31, b'sent moderation alert')])),
                ('active_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('is_auditted', models.BooleanField(default=False)),
                ('summary', models.TextField(default=b'')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'activity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityAuditStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'new'), (1, b'seen')])),
                ('activity', models.ForeignKey(to='askbot.Activity', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'askbot_activityauditstatus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnonymousAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_key', models.CharField(max_length=40)),
                ('wiki', models.BooleanField(default=False)),
                ('added_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('ip_addr', models.GenericIPAddressField()),
                ('text', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnonymousQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_key', models.CharField(max_length=40)),
                ('wiki', models.BooleanField(default=False)),
                ('added_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('ip_addr', models.GenericIPAddressField()),
                ('text', models.TextField()),
                ('title', models.CharField(max_length=300)),
                ('tagnames', models.CharField(max_length=125)),
                ('is_anonymous', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AskWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('include_text_field', models.BooleanField(default=False)),
                ('inner_style', models.TextField(blank=True)),
                ('outer_style', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('awarded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('notified', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'award',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BadgeData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True)),
                ('awarded_count', models.PositiveIntegerField(default=0)),
                ('display_order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('display_order', 'slug'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BulkTagSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date_added'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DraftAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DraftQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=300, null=True)),
                ('text', models.TextField(null=True)),
                ('tagnames', models.CharField(max_length=125, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailFeedSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feed_type', models.CharField(max_length=16, choices=[(b'q_all', 'Entire forum'), (b'q_ask', 'Questions that I asked'), (b'q_ans', 'Questions that I answered'), (b'q_sel', 'Individually selected questions'), (b'm_and_c', 'Mentions and comment responses')])),
                ('frequency', models.CharField(default=b'n', max_length=8, choices=[(b'i', 'instantly'), (b'd', 'daily'), (b'w', 'weekly'), (b'n', 'no email')])),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('reported_at', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FavoriteQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'favorite_question',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='auth.Group', on_delete=models.CASCADE)),
                ('logo_url', models.URLField(null=True)),
                ('moderate_email', models.BooleanField(default=True)),
                ('moderate_answers_to_enquirers', models.BooleanField(default=False, help_text=b'If true, answers to outsiders questions will be shown to the enquirers only when selected by the group moderators.')),
                ('openness', models.SmallIntegerField(default=2, choices=[(0, b'open'), (1, b'moderated'), (2, b'closed')])),
                ('preapproved_emails', models.TextField(default=b'', null=True, blank=True)),
                ('preapproved_email_domains', models.TextField(default=b'', null=True, blank=True)),
                ('is_vip', models.BooleanField(default=False, help_text=b'Check to make members of this group site moderators')),
                ('read_only', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'askbot_group',
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.SmallIntegerField(default=1, choices=[(0, b'pending'), (1, b'full')])),
                ('group', models.ForeignKey(related_name='user_membership', to='auth.Group', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImportedObjectInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_id', models.IntegerField(help_text=b'Old object id in the source database')),
                ('new_id', models.IntegerField(help_text=b'New object id in the current database')),
                ('model', models.CharField(default=b'', help_text=b'dotted python path to model', max_length=255)),
                ('extra_info', picklefield.fields.PickledObjectField(help_text=b'to hold dictionary for various data', editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImportRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('command', models.TextField(default=b'')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MarkedTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.CharField(max_length=16, choices=[(b'good', 'interesting'), (b'bad', 'ignored'), (b'subscribed', 'subscribed')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(verbose_name='message')),
            ],
            options={
                'db_table': 'askbot_message',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_type', models.CharField(max_length=255, db_index=True)),
                ('old_question_id', models.PositiveIntegerField(default=None, unique=True, null=True, blank=True)),
                ('old_answer_id', models.PositiveIntegerField(default=None, unique=True, null=True, blank=True)),
                ('old_comment_id', models.PositiveIntegerField(default=None, unique=True, null=True, blank=True)),
                ('added_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('endorsed', models.BooleanField(default=False, db_index=True)),
                ('endorsed_at', models.DateTimeField(null=True, blank=True)),
                ('approved', models.BooleanField(default=True, db_index=True)),
                ('deleted', models.BooleanField(default=False, db_index=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('wiki', models.BooleanField(default=False)),
                ('wikified_at', models.DateTimeField(null=True, blank=True)),
                ('locked', models.BooleanField(default=False)),
                ('locked_at', models.DateTimeField(null=True, blank=True)),
                ('points', models.IntegerField(default=0, db_column='score')),
                ('vote_up_count', models.IntegerField(default=0)),
                ('vote_down_count', models.IntegerField(default=0)),
                ('comment_count', models.PositiveIntegerField(default=0)),
                ('offensive_flag_count', models.SmallIntegerField(default=0)),
                ('last_edited_at', models.DateTimeField(null=True, blank=True)),
                ('html', models.TextField(null=True)),
                ('text', models.TextField(null=True)),
                ('language_code', models.CharField(default=b'en', max_length=16, choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('summary', models.TextField(null=True)),
                ('is_anonymous', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'askbot_post',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostFlagReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added_at', models.DateTimeField()),
                ('title', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.PositiveIntegerField()),
                ('revised_at', models.DateTimeField()),
                ('summary', models.CharField(max_length=300, blank=True)),
                ('text', models.TextField(blank=True)),
                ('approved', models.BooleanField(default=False, db_index=True)),
                ('approved_at', models.DateTimeField(null=True, blank=True)),
                ('by_email', models.BooleanField(default=False)),
                ('email_address', models.EmailField(max_length=75, null=True, blank=True)),
                ('title', models.CharField(default=b'', max_length=300, blank=True)),
                ('tagnames', models.CharField(default=b'', max_length=125, blank=True)),
                ('is_anonymous', models.BooleanField(default=False)),
                ('ip_addr', models.GenericIPAddressField(default=b'0.0.0.0', db_index=True)),
            ],
            options={
                'ordering': ('-revision',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostToGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='askbot.Group', on_delete=models.CASCADE)),
                ('post', models.ForeignKey(to='askbot.Post', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'askbot_post_groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField()),
                ('question', models.ForeignKey(related_name='viewed', to='askbot.Post', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('question_number', models.PositiveIntegerField(default=7)),
                ('tagnames', models.CharField(max_length=50, verbose_name='tags')),
                ('search_query', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('order_by', models.CharField(default=b'-added_at', max_length=18, choices=[(b'-added_at', 'date descendant'), (b'added_at', 'date ascendant'), (b'-last_activity_at', 'most recently active'), (b'last_activity_at', 'least recently active'), (b'-answer_count', 'more responses'), (b'answer_count', 'fewer responses'), (b'-points', 'more votes'), (b'points', 'less votes')])),
                ('style', models.TextField(default=b"\n@import url('http://fonts.googleapis.com/css?family=Yanone+Kaffeesatz:300,400,700');\nbody {\n    overflow: hidden;\n}\n\n#container {\n    width: 200px;\n    height: 350px;\n}\nul {\n    list-style: none;\n    padding: 5px;\n    margin: 5px;\n}\nli {\n    border-bottom: #CCC 1px solid;\n    padding-bottom: 5px;\n    padding-top: 5px;\n}\nli:last-child {\n    border: none;\n}\na {\n    text-decoration: none;\n    color: #464646;\n    font-family: 'Yanone Kaffeesatz', sans-serif;\n    font-size: 15px;\n}\n", verbose_name='css for the widget', blank=True)),
                ('group', models.ForeignKey(blank=True, to='askbot.Group', null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReplyAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(unique=True, max_length=25)),
                ('reply_action', models.CharField(default=b'auto_answer_or_comment', max_length=32, choices=[(b'post_answer', b'Post an answer'), (b'post_comment', b'Post a comment'), (b'replace_content', b'Edit post'), (b'append_content', b'Append to post'), (b'auto_answer_or_comment', b'Answer or comment, depending on the size of post'), (b'validate_email', b'Validate email and record signature')])),
                ('allowed_from_email', models.EmailField(max_length=150)),
                ('used_at', models.DateTimeField(default=None, null=True)),
                ('post', models.ForeignKey(related_name='reply_addresses', to='askbot.Post', null=True, on_delete=models.CASCADE)),
                ('response_post', models.ForeignKey(related_name='edit_addresses', to='askbot.Post', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'askbot_replyaddress',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Repute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('positive', models.SmallIntegerField(default=0)),
                ('negative', models.SmallIntegerField(default=0)),
                ('reputed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('reputation_type', models.SmallIntegerField(choices=[(1, b'gain_by_upvoted'), (2, b'gain_by_answer_accepted'), (3, b'gain_by_accepting_answer'), (4, b'gain_by_downvote_canceled'), (5, b'gain_by_canceling_downvote'), (-1, b'lose_by_canceling_accepted_answer'), (-2, b'lose_by_accepted_answer_cancled'), (-3, b'lose_by_downvoted'), (-4, b'lose_by_flagged'), (-5, b'lose_by_downvoting'), (-6, b'lose_by_flagged_lastrevision_3_times'), (-7, b'lose_by_flagged_lastrevision_5_times'), (-8, b'lose_by_upvote_canceled'), (10, b'assigned_by_moderator')])),
                ('reputation', models.IntegerField(default=1)),
                ('comment', models.CharField(max_length=128, null=True)),
                ('question', models.ForeignKey(blank=True, to='askbot.Post', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'repute',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('language_code', models.CharField(default=b'en', max_length=16, choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('status', models.SmallIntegerField(default=1)),
                ('used_count', models.PositiveIntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ('-used_count', 'name'),
                'db_table': 'tag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagSynonym',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_tag_name', models.CharField(unique=True, max_length=255)),
                ('target_tag_name', models.CharField(max_length=255, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('auto_rename_count', models.IntegerField(default=0)),
                ('last_auto_rename_at', models.DateTimeField(auto_now=True)),
                ('language_code', models.CharField(default=b'en', max_length=16, choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=300)),
                ('tagnames', models.CharField(max_length=125)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('favourite_count', models.PositiveIntegerField(default=0)),
                ('answer_count', models.PositiveIntegerField(default=0)),
                ('last_activity_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('language_code', models.CharField(default=b'en', max_length=16, choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('closed', models.BooleanField(default=False)),
                ('closed_at', models.DateTimeField(null=True, blank=True)),
                ('close_reason', models.SmallIntegerField(blank=True, null=True, choices=[(1, 'duplicate question'), (2, 'question is off-topic or not relevant'), (3, 'too subjective and argumentative'), (4, 'not a real question'), (5, 'the question is answered, right answer was accepted'), (6, 'question is not relevant or outdated'), (7, 'question contains offensive or malicious remarks'), (8, 'spam or advertising'), (9, 'too localized')])),
                ('deleted', models.BooleanField(default=False, db_index=True)),
                ('approved', models.BooleanField(default=True, db_index=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('points', models.IntegerField(default=0, db_column='score')),
                ('accepted_answer', models.ForeignKey(related_name='+', blank=True, to='askbot.Post', null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ThreadToGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visibility', models.SmallIntegerField(default=1, choices=[(0, b'show only published responses'), (1, b'show all responses')])),
                ('group', models.ForeignKey(to='askbot.Group', on_delete=models.CASCADE)),
                ('thread', models.ForeignKey(to='askbot.Thread', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'askbot_thread_groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('auth_user_ptr', models.OneToOneField(parent_link=True, related_name='askbot_profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('avatar_urls', jsonfield.fields.JSONField(default={})),
                ('status', models.CharField(default=b'w', max_length=2, choices=[(b'd', 'administrator'), (b'm', 'moderator'), (b'a', 'approved'), (b'w', 'watched'), (b's', 'suspended'), (b'b', 'blocked')])),
                ('is_fake', models.BooleanField(default=False)),
                ('email_isvalid', models.BooleanField(default=False)),
                ('email_key', models.CharField(max_length=32, null=True)),
                ('reputation', models.PositiveIntegerField(default=1)),
                ('gravatar', models.CharField(max_length=32)),
                ('avatar_type', models.CharField(default=b'n', max_length=1, choices=[(b'n', 'Default avatar'), (b'g', 'Gravatar'), (b'a', 'Uploaded Avatar')])),
                ('gold', models.SmallIntegerField(default=0)),
                ('silver', models.SmallIntegerField(default=0)),
                ('bronze', models.SmallIntegerField(default=0)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('real_name', models.CharField(max_length=100, blank=True)),
                ('website', models.URLField(blank=True)),
                ('location', models.CharField(max_length=100, blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('show_country', models.BooleanField(default=False)),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('about', models.TextField(blank=True)),
                ('interesting_tags', models.TextField(blank=True)),
                ('ignored_tags', models.TextField(blank=True)),
                ('subscribed_tags', models.TextField(blank=True)),
                ('email_signature', models.TextField(blank=True)),
                ('show_marked_tags', models.BooleanField(default=True)),
                ('email_tag_filter_strategy', models.SmallIntegerField(default=1, choices=[(0, 'email for all tags'), (1, 'exclude ignored tags'), (2, 'only interesting tags'), (3, 'only subscribed tags')])),
                ('display_tag_filter_strategy', models.SmallIntegerField(default=0, choices=[(0, 'show all tags'), (1, 'exclude ignored tags'), (2, 'only interesting tags'), (3, 'only subscribed tags')])),
                ('new_response_count', models.IntegerField(default=0)),
                ('seen_response_count', models.IntegerField(default=0)),
                ('consecutive_days_visit_count', models.IntegerField(default=0)),
                ('languages', models.CharField(default=b'en', max_length=128)),
                ('twitter_access_token', models.CharField(default=b'', max_length=256)),
                ('twitter_handle', models.CharField(default=b'', max_length=32)),
                ('social_sharing_mode', models.IntegerField(default=0, choices=[(0, 'disable sharing'), (1, 'my posts'), (2, 'all posts')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])),
                ('voted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(related_name='votes', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('voted_post', models.ForeignKey(related_name='votes', to='askbot.Post', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'vote',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('user', 'voted_post')]),
        ),
        migrations.AlterUniqueTogether(
            name='threadtogroup',
            unique_together=set([('thread', 'group')]),
        ),
        migrations.AddField(
            model_name='thread',
            name='closed_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='favorited_by',
            field=models.ManyToManyField(related_name='unused_favorite_threads', through='askbot.FavoriteQuestion', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='followed_by',
            field=models.ManyToManyField(related_name='followed_threads', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='groups',
            field=models.ManyToManyField(related_name='group_threads', through='askbot.ThreadToGroup', to='askbot.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='last_activity_by',
            field=models.ForeignKey(related_name='unused_last_active_in_threads', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='tags',
            field=models.ManyToManyField(related_name='threads', to='askbot.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagsynonym',
            name='owned_by',
            field=models.ForeignKey(related_name='tag_synonyms', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='created_by',
            field=models.ForeignKey(related_name='created_tags', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='deleted_by',
            field=models.ForeignKey(related_name='deleted_tags', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='suggested_by',
            field=models.ManyToManyField(help_text=b'Works only for suggested tags for tag moderation', related_name='suggested_tags', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='tag_wiki',
            field=models.OneToOneField(related_name='described_tag', null=True, to='askbot.Post', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'language_code')]),
        ),
        migrations.AddField(
            model_name='repute',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='replyaddress',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionview',
            name='who',
            field=models.ForeignKey(related_name='question_views', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='posttogroup',
            unique_together=set([('post', 'group')]),
        ),
        migrations.AddField(
            model_name='postrevision',
            name='approved_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='postrevision',
            name='author',
            field=models.ForeignKey(related_name='postrevisions', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='postrevision',
            name='post',
            field=models.ForeignKey(related_name='revisions', blank=True, to='askbot.Post', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='postrevision',
            unique_together=set([('post', 'revision')]),
        ),
        migrations.AddField(
            model_name='postflagreason',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='postflagreason',
            name='details',
            field=models.ForeignKey(related_name='post_reject_reasons', to='askbot.Post', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(related_name='posts', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='current_revision',
            field=models.ForeignKey(related_name='rendered_posts', blank=True, to='askbot.PostRevision', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='deleted_by',
            field=models.ForeignKey(related_name='deleted_posts', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='endorsed_by',
            field=models.ForeignKey(related_name='endorsed_posts', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='groups',
            field=models.ManyToManyField(related_name='group_posts', through='askbot.PostToGroup', to='askbot.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='last_edited_by',
            field=models.ForeignKey(related_name='last_edited_posts', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='locked_by',
            field=models.ForeignKey(related_name='locked_posts', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(related_name='comments', blank=True, to='askbot.Post', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(related_name='posts', default=None, blank=True, to='askbot.Thread', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(related_name='_message_set', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='markedtag',
            name='tag',
            field=models.ForeignKey(related_name='user_selections', to='askbot.Tag', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='markedtag',
            name='user',
            field=models.ForeignKey(related_name='tag_selections', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='importedobjectinfo',
            name='run',
            field=models.ForeignKey(to='askbot.ImportRun', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupmembership',
            name='user',
            field=models.ForeignKey(related_name='group_membership', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='groupmembership',
            unique_together=set([('group', 'user')]),
        ),
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.OneToOneField(related_name='described_group', null=True, blank=True, to='askbot.Post', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favoritequestion',
            name='thread',
            field=models.ForeignKey(to='askbot.Thread', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favoritequestion',
            name='user',
            field=models.ForeignKey(related_name='user_favorite_questions', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='emailfeedsetting',
            name='subscriber',
            field=models.ForeignKey(related_name='notification_subscriptions', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='emailfeedsetting',
            unique_together=set([('subscriber', 'feed_type')]),
        ),
        migrations.AddField(
            model_name='draftquestion',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='draftanswer',
            name='author',
            field=models.ForeignKey(related_name='draft_answers', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='draftanswer',
            name='thread',
            field=models.ForeignKey(related_name='draft_answers', to='askbot.Thread', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bulktagsubscription',
            name='groups',
            field=models.ManyToManyField(to='askbot.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bulktagsubscription',
            name='tags',
            field=models.ManyToManyField(to='askbot.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bulktagsubscription',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='badgedata',
            name='awarded_to',
            field=models.ManyToManyField(related_name='badges', through='askbot.Award', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='badge',
            field=models.ForeignKey(related_name='award_badge', to='askbot.BadgeData', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='user',
            field=models.ForeignKey(related_name='award_user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='askwidget',
            name='group',
            field=models.ForeignKey(blank=True, to='askbot.Group', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='askwidget',
            name='tag',
            field=models.ForeignKey(blank=True, to='askbot.Tag', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='anonymousquestion',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='anonymousanswer',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='anonymousanswer',
            name='question',
            field=models.ForeignKey(related_name='anonymous_answers', to='askbot.Post', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activityauditstatus',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='activityauditstatus',
            unique_together=set([('user', 'activity')]),
        ),
        migrations.AddField(
            model_name='activity',
            name='question',
            field=models.ForeignKey(to='askbot.Post', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='recipients',
            field=models.ManyToManyField(related_name='incoming_activity', through='askbot.ActivityAuditStatus', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
