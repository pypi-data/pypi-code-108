import uuid
import json
from rest_framework.test import APITestCase, APIClient

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

    def test_post_joboffer(self):
        self.setUpLoggedInUser()

        body = {
            "closingDate": "2022-01-27",
            "title": "Most cool php offer",
            "description": "So cool\\n",
            "skills": {
                "ldp:contains": [
                    { "@id": "https://api.test1.startinblox.com/skills/3/" },
                    { "@id": "https://api.test1.startinblox.com/skills/1/" },
                    { "@id": "https://api.test1.startinblox.com/skills/4/" }
                ]
            },
            "budget": 12000,
            "duration": "1 Month",
            "location": "",
            "earnBusinessProviding": False,
            "@context": {"@vocab": "http://happy-dev.fr/owl/#", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "ldp": "http://www.w3.org/ns/ldp#", "foaf": "http://xmlns.com/foaf/0.1/", "name": "rdfs:label", "acl": "http://www.w3.org/ns/auth/acl#", "permissions": "acl:accessControl", "mode": "acl:mode", "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "lat":"geo:lat","lng":"geo:long","inbox":"http://happy-dev.fr/owl/#inbox","object":"http://happy-dev.fr/owl/#object","author":"http://happy-dev.fr/owl/#author","account":"http://happy-dev.fr/owl/#account","jabberID":"foaf:jabberID"}
        }

        response = self.client.post('/job-offers/', data=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
