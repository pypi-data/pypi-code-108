import uuid
import json
from django.conf import settings
from rest_framework.test import APITestCase, APIClient

from djangoldp.models import Model, Activity
from djangoldp_notification.models import Notification, Subscription
from djangoldp_skill.models import Skill
from djangoldp_joboffer.models import JobOffer
from djangoldp_account.models import LDPUser


class TestNotifications(APITestCase):
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

    '''
    We want it to be fired when skills are added to the JobOffer
		We do not want to repeat ourselves (reuse ActivityQueue logic or store old skills redundancy)
			You could store the old skills redundancy when the notification is sent :-)

	We will fire a custom signal when all the skills have been added to a JobOffer via the Serializer
		We will also fire this signal when the JobOffer is updated via the admin panel
    '''

    # I posted a new JobOffer matching a user's skills
    def test_create_joboffer_notifications(self):
        # set up users and target skill
        skill_a = Skill.objects.create()
        skill_b = Skill.objects.create()

        # one will be notified
        user_match = self._get_random_user()
        user_match.skills.add(skill_a)
        # one will not have the right skill
        user_nomatch = self._get_random_user()
        user_nomatch.skills.add(skill_b)
        # the author of the JobOffer will not be notified
        self.setUpLoggedInUser()
        self.user.skills.add(skill_a)
        self.user.skills.add(skill_b)

        # a distant server will be watching our job notifications
        Subscription.objects.create(object='{}/job-offers/'.format(settings.BASE_URL), inbox='http://localhost:8001/inbox/', disable_automatic_notifications=True)
        self.assertEqual(Activity.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)

        body = {
            'http://happy-dev.fr/owl/#title': "new job",
            'http://happy-dev.fr/owl/#slug': "job1",
            'http://happy-dev.fr/owl/#author': {
                '@id': self.user.urlid
            },
            'http://happy-dev.fr/owl/#skills': {
                "ldp:contains": [
                    {"@id": skill_a.urlid},
                ]
            }
        }

        response = self.client.post('/job-offers/',
                                    data=json.dumps(body),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        # assert which local users have been notified
        self.assertEqual(user_match.inbox.count(), 1)
        self.assertEqual(user_nomatch.inbox.count(), 0)
        self.assertEqual(self.user.inbox.count(), 0)
        self.assertEqual(Notification.objects.count(), 1)

        # an activity has been created to notify the distant subscriber
        self.assertEqual(Activity.objects.filter(external_id='http://localhost:8001/inbox/').count(), 1)
        # NOTE: some other activities are created but this is due to the test server's confusion about whether it is running on localhost or testserver
        # self.assertEqual(Activity.objects.count(), 1)

    # I updated the skills on an existing JobOffer
    def test_update_joboffer_notifications(self):
        self.setUpLoggedInUser()

        # set up pre-existing skill and JobOffer
        skill = Skill.objects.create()
        job_offer = JobOffer.objects.create(author=self.user)
        job_offer.skills.add(skill)

        # set up a user which has been notified about the job offer, and one who has not
        user_notified = self._get_random_user()
        user_notified.skills.add(skill)

        skill_b = Skill.objects.create()
        user_to_be_notified = self._get_random_user()
        user_to_be_notified.skills.add(skill_b)

        # pretend that we have already notified one of these users, and not the other
        Notification.objects.create(user=user_notified, author='{}/job-offers/'.format(settings.BASE_URL), object=job_offer.urlid, type='creation')
        self.assertEqual(user_notified.inbox.count(), 1)
        self.assertEqual(user_to_be_notified.inbox.count(), 0)

        # a distant server will be watching our job notifications
        Subscription.objects.create(object='{}/job-offers/'.format(settings.BASE_URL), inbox='http://localhost:8001/inbox/', disable_automatic_notifications=True)
        self.assertEqual(Notification.objects.count(), 1)

        body = {
            '@context': 'https://cdn.happy-dev.fr/owl/hdcontext.jsonld',
            '@id': job_offer.urlid,
            'title': 'Test',
            'http://happy-dev.fr/owl/#skills': {
                "ldp:contains": [
                    {"@id": skill.urlid},
                    {"@id": skill_b.urlid}
                ]
            }
        }

        response = self.client.put('/job-offers/{}/'.format(job_offer.pk),
                                    data=json.dumps(body),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        # assert that no duplicate notification was fired for the user already notified
        self.assertEqual(user_notified.inbox.count(), 1)
        # but that a new notification was sent to the user which had not been notified before
        self.assertEqual(user_to_be_notified.inbox.count(), 1)
        self.assertEqual(Notification.objects.count(), 2)

        # an activity has been created to notify the distant subscriber
        self.assertEqual(Activity.objects.filter(external_id='http://localhost:8001/inbox/').count(), 1)

    # TODO: it is not resending the activity if skills have not changed
    # TODO: it is resending the activity if the skills have changed
