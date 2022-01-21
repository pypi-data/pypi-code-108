from askbot import models
from askbot.tests.utils import AskbotTestCase

from django.test.client import Client
from django.conf import settings as django_settings
from django.urls import reverse
from django.utils import translation, timezone
import unittest
from django.test import signals

def patch_jinja2():
    from jinja2 import Template
    ORIG_JINJA2_RENDERER = Template.render

    def instrumented_render(template_object, *args, **kwargs):
        context = dict(*args, **kwargs)
        signals.template_rendered.send(
                                sender=template_object,
                                template=template_object,
                                context=context
                            )
        return ORIG_JINJA2_RENDERER(template_object, *args, **kwargs)
    Template.render = instrumented_render

patch_jinja2()


class WidgetViewsTests(AskbotTestCase):

    def setUp(self):
        translation.activate(django_settings.LANGUAGE_CODE)
        self.client = Client()
        self.widget = models.AskWidget.objects.create(title='foo widget')
        self.user = self.create_user('user1')
        self.user.set_password('sample')
        self.user.save()
        self.good_data = {'title': 'This is a title question',
                          'ask_anonymously': False}

    @unittest.skip('widgets are disabled')
    def test_post_with_auth(self):
        self.client.login(username='user1', password='sample')
        response = self.client.post(reverse('ask_by_widget', args=(self.widget.id, )), self.good_data)
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    @unittest.skip('widgets are disabled')
    def test_post_without_auth(self):
        #weird issue
        response = self.client.post(reverse('ask_by_widget', args=(self.widget.id, )), self.good_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('widget_question' in self.client.session)
        self.assertEqual(self.client.session['widget_question']['title'],
                          self.good_data['title'])

    @unittest.skip('widgets are disabled')
    def test_post_after_login(self):
        widget_question_data = { 'title': 'testing post after login, does it?',
                                 'author': self.user,
                                 'added_at': timezone.now(),
                                 'wiki': False,
                                 'text': ' ',
                                 'tagnames': '',
                                 'is_anonymous': False
                               }

        self.client.login(username='user1', password='sample')

        session = self.client.session
        session['widget_question'] = widget_question_data
        session.save()
        response = self.client.get(
            reverse('ask_by_widget', args=(self.widget.id, )),
            {'action': 'post-after-login'}
        )
        self.assertFalse('widget_question' in self.client.session)
        self.assertEqual(response.status_code, 302)
        #verify posting question

    @unittest.skip('widgets are disabled')
    def test_render_widget_view(self):
        response = self.client.get(reverse('render_ask_widget', args=(self.widget.id, )))
        self.assertEqual(200, response.status_code)
        content_type = 'text/javascript'
        self.assertTrue(content_type in response['Content-Type'])


class WidgetLoginViewTest(AskbotTestCase):

    @unittest.skip('widgets are disabled')
    def test_correct_template_loading(self):
        client = Client()
        response = client.get(reverse('widget_signin'))
        template_name = 'authopenid/widget_signin.html'
        templates = [template.name for template in response.templates]
        self.assertTrue(template_name in templates)

class WidgetCreatorViewsTests(AskbotTestCase):

    def setUp(self):
        translation.activate(django_settings.LANGUAGE_CODE)
        self.client = Client()
        self.user = self.create_user('user1')
        self.user.set_password('testpass')
        self.user.set_status('d')
        self.user.save()
        self.widget = models.AskWidget.objects.create(title='foo widget')

    @unittest.skip('widgets are disabled')
    def test_list_ask_widget_view(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.get(reverse('list_widgets', args=('ask',)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('widgets' in response.context)

    @unittest.skip('widgets are disabled')
    def test_create_ask_widget_get(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.get(reverse('create_widget', args=('ask',)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    @unittest.skip('widgets are disabled')
    def test_create_ask_widget_post(self):
        self.client.login(username='user1', password='testpass')
        post_data = {'title': 'Test widget'}
        response = self.client.post(reverse('create_widget', args=('ask',)), post_data)
        self.assertEqual(response.status_code, 302)

    @unittest.skip('widgets are disabled')
    def test_edit_ask_widget_get(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.get(reverse('edit_widget',
            args=('ask', self.widget.id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    @unittest.skip('widgets are disabled')
    def test_edit_ask_widget_post(self):
        self.client.login(username='user1', password='testpass')
        post_data = {'title': 'Test lalalla'}
        response = self.client.post(reverse('edit_widget',
            args=('ask', self.widget.id, )), post_data)
        self.assertEqual(response.status_code, 302)

    @unittest.skip('widgets are disabled')
    def test_delete_ask_widget_get(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.get(reverse('delete_widget',
            args=('ask', self.widget.id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('widget' in response.context)

    @unittest.skip('widgets are disabled')
    def test_delete_ask_widget_post(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.post(reverse('delete_widget',
            args=('ask', self.widget.id, )))
        self.assertEqual(response.status_code, 302)

    #this test complains about 404.html template but it's correct
    #def test_bad_url(self):
    #    self.client.login(username='user1', password='testpass')
    #    response = self.client.get('/widgets/foo/create/')
    #    self.assertEquals(404, response.status_code)


class QuestionWidgetViewsTests(AskbotTestCase):

    def setUp(self):
        translation.activate(django_settings.LANGUAGE_CODE)
        self.user = self.create_user('testuser')
        self.client = Client()
        self.widget =  models.QuestionWidget.objects.create(title="foo",
                                   question_number=5, search_query='test',
                                   tagnames='test')

        #we post 6 questions!
        titles = (
            'test question 1', 'this is a test',
            'without the magic word', 'test test test',
            'test just another test', 'no magic word',
            'test another', 'I can no believe is a test'
        )

        tagnames = 'test foo bar'
        for title in titles:
            self.post_question(title=title, tags=tagnames)

    @unittest.skip('widgets are disabled')
    def test_valid_response(self):
        filter_params = {
            'title__icontains': self.widget.search_query,
            'tags__name__in': self.widget.tagnames.split(' ')
        }
        threads = models.Thread.objects.filter(**filter_params).order_by(self.widget.order_by)[:5]
        # threads = models.Thread.objects.filter(**filter_params)[:5]

        response = self.client.get(reverse('question_widget', args=(self.widget.id, )))
        self.assertEqual(200, response.status_code)

        self.assertQuerysetEqual(threads, response.context['threads'], transform=lambda x: x)
        self.assertEqual(self.widget, response.context['widget'])
