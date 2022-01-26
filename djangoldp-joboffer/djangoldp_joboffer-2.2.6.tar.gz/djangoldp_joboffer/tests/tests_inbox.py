import uuid
import json
from datetime import date
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient

from djangoldp.models import Model
from djangoldp_notification.models import Notification, send_request
from djangoldp_skill.models import Skill
from djangoldp_joboffer.models import JobOffer
from djangoldp_account.models import LDPUser


class TestInbox(APITestCase):
    def _get_random_user(self):
        return LDPUser.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test',
                                      last_name='Test', username=str(uuid.uuid4()))

    def _auth_as_user(self, user):
        self.client.force_authenticate(user=user)

    def setUpLoggedInUser(self):
        self.user = LDPUser.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test',
                                           last_name='Test', username='admin', urlid='http://testserver/users/admin/')
        self._auth_as_user(self.user)

    def setUp(self):
        self.client = APIClient()

    def _get_notification_json(self, urlid, skills=[]):
        return {
            "@context": "https://cdn.happy-dev.fr/owl/hdcontext.jsonld",
            "object": {
                "@id": urlid,
                "@type": Model.get_meta(JobOffer, 'rdf_type'),
                'title': "Test",
                'description': "Description",
                'location': "Paris",
                'budget': "10,000 €",
                'closingDate': date.today().strftime("%Y-%m-%d"),
                "skills": {
                    '@type': 'ldp:Container',
                    'ldp:contains': ','.join([skill.urlid for skill in skills])
                }
            },
            "author": "https://distant.com/users/abc/",
            "type": "JobOffer",
            "summary": "Hello"
        }

    # test endpoint allowing me to send a notification to all users on the server
    def test_notify_all_users_view(self):
        # set up a job offer with a skill
        skill = Skill.objects.create(name='Skill')
        # job_offer = JobOffer.objects.create(urlid='https://api.test2.startinblox.com/job-offers/1/')
        # job_offer.skills.add(skill)

        # set up two users with the appropriate skills and one without
        user_a = self._get_random_user()
        user_a.skills.add(skill)
        user_b = self._get_random_user()
        user_b.skills.add(skill)
        user_c = self._get_random_user()

        # two users should be notified, others not
        data = self._get_notification_json(urlid='https://api.test2.startinblox.com/job-offers/1/', skills=[skill])
        response = self.client.post(
            '/job-offers/inbox/',
            data=json.dumps(data),
            content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(user_a.inbox.count(), 1)
        self.assertEqual(user_b.inbox.count(), 1)
        self.assertEqual(user_c.inbox.count(), 0)
        self.assertEqual(JobOffer.objects.count(), 1)
        job_offer = JobOffer.objects.all()[0]
        self.assertEqual(job_offer.title, data['object']['title'])

        # resend the notification, and assert that the user is not notified about it again
        response = self.client.post(
            '/job-offers/inbox/',
            data=json.dumps(data),
            content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(user_a.inbox.count(), 1)
        self.assertEqual(user_b.inbox.count(), 1)
        self.assertEqual(user_c.inbox.count(), 0)
        self.assertEqual(JobOffer.objects.count(), 1)
