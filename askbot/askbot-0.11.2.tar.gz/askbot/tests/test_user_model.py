from askbot.tests.utils import AskbotTestCase, with_settings
from django.contrib.auth.models import User
from askbot import models
from askbot.conf import settings
from askbot import signals
from askbot.models.tag import format_personal_group_name
from askbot.models.user import get_invited_moderators

INVITED_MODS = """one@example.com One User
broken user without email
two@example.com Two User"""

class UserModelTests(AskbotTestCase):
    """test user model"""

    def test_get_invited_moderators0(self):
        mods = get_invited_moderators()
        self.assertEqual(len(mods), 0)

    @with_settings(INVITED_MODERATORS=INVITED_MODS)
    def test_get_invited_moderators1(self):
        mods = get_invited_moderators()
        self.assertEqual(len(mods), 2)

        emails = set([m.email for m in mods])
        self.assertEqual(emails, set(['one@example.com', 'two@example.com']))

        names = set([m.username for m in mods])
        self.assertEqual(names, set(['One User', 'Two User']))


    @with_settings(INVITED_MODERATORS=INVITED_MODS)
    def test_get_invited_moderators2(self):
        u = self.create_user('One User', 'one@example.com')
        mods = get_invited_moderators()
        self.assertEqual(len(mods), 1)

        emails = set([m.email for m in mods])
        self.assertEqual(emails, set(['two@example.com',]))

        names = set([m.username for m in mods])
        self.assertEqual(names, set(['Two User',]))


    @with_settings(INVITED_MODERATORS=INVITED_MODS)
    def test_invited_mod_removed_from_setting_upon_joining(self):
        # we need one more user so that it's made admin
        # and that the next user is not automatically made an admin
        admin = self.create_user('Admin', 'admin@example.com')
        self.assertEqual(len(settings.INVITED_MODERATORS.split('\n')), 3)
        u = self.create_user('One User', 'one@example.com')
        self.assertEqual(len(settings.INVITED_MODERATORS.split('\n')), 2)
        u = self.reload_object(u)
        self.assertEqual(u.status, 'm')


    def test_new_user_has_personal_group(self):
        user = User.objects.create_user('somebody', 'somebody@example.com')
        group_name = format_personal_group_name(user)
        group = models.Group.objects.get(name=group_name)
        memberships = models.GroupMembership.objects.get(
                                                group=group, user=user
                                            )

    def test_new_user_has_subscriptions(self):
        old_value = settings.SUBSCRIBED_TAG_SELECTOR_ENABLED
        old_group_value = settings.GROUPS_ENABLED
        settings.SUBSCRIBED_TAG_SELECTOR_ENABLED = True
        settings.GROUPS_ENABLED = True
        one_tag  = self.create_tag('one-tag')
        another_tag  = self.create_tag('another_tag')

        global_group =  models.Group.objects.get_global_group()

        the_boss = self.create_user('theboss')
        bulk_subscription = models.BulkTagSubscription.objects.create(
                                                tag_names=[one_tag.name, another_tag.name],
                                                group_list=[global_group],
                                                tag_author=the_boss,
                                                language_code='en'
                                            )

        user = self.create_user('someone')
        marked_tags = user.get_marked_tags('subscribed')
        self.assertTrue(one_tag in marked_tags)
        self.assertTrue(another_tag in marked_tags)
        settings.SUBSCRIBED_TAG_SELECTOR_ENABLED = old_value
        settings.GROUPS_ENABLED = old_group_value

    def test_delete_user(self):
        user = self.create_user('user')
        user.delete()
        self.assertRaises(User.DoesNotExist, User.objects.get, username='user')

    def test_rename_user(self):
        user = self.create_user('user')
        user.username = 'user2'
        user.save()
