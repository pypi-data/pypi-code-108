import uuid
import json

from rest_framework.test import APITestCase, APIClient

from djangoldp_energiepartagee.models import *
from djangoldp_energiepartagee.tests.models import User


class PermissionsTestCase(APITestCase):
    # Django runs setUp automatically before every test
    def setUp(self):
        self.client = APIClient()

    # we have custom set up functions for things that we don't want to run before *every* test, e.g. often we want to
    # set up an authenticated user, but sometimes we want to run a test with an anonymous user
    def setUpLoggedInUser(self, is_superuser=False):
        self.user = User(email='test@mactest.co.uk', first_name='Test', last_name='Mactest', username='test',
                         password='glass onion', is_superuser=is_superuser)
        self.user.save()
        # this means that our user is now logged in (as if they had typed username and password)
        self.client.force_authenticate(user=self.user)

    def setUpActor(self, owner_user=None):
        region = self._get_random_region()
        college = self._get_random_college()
        another_user = self._get_random_user()
        self.actor = self._get_random_actor(region, college, another_user, owner_user=owner_user)

    def setUpContribution(self):
        regionalnetwork = self._get_random_regionalnetwork()
        paymentmethod = self._get_random_paymentmethod()
        self.contribution = self._get_random_contribution(self.actor, regionalnetwork, paymentmethod)

    def _get_request_json(self, **kwargs):
        res = {
            '@context': {
                'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
                'name': "rdfs:label",
                'isocode': "http://happy-dev.fr/owl/#isocode",
                'year': "http://happy-dev.fr/owl/#year",
                'amount': "http://happy-dev.fr/owl/#amount",
                'actor': "http://happy-dev.fr/owl/#actor",
                'presentation': "http://happy-dev.fr/owl/#presentation",
                'user': "http://happy-dev.fr/owl/#user",
                'postcode': "http://happy-dev.fr/owl/#postcode",
                'shortname': "http://happy-dev.fr/owl/#shortname",
                'longname': "http://happy-dev.fr/owl/#longname",
                'adhesiondate': "http://happy-dev.fr/owl/#adhesiondate",
                'mail': "http://happy-dev.fr/owl/#mail",
                'adhmail': "http://happy-dev.fr/owl/#adhmail",
                'address': "http://happy-dev.fr/owl/#address",
                'legalrepresentant': "http://happy-dev.fr/owl/#legalrepresentant",
                'managementcontact': "http://happy-dev.fr/owl/#managementcontact",
                'region': "http://happy-dev.fr/owl/#region",
                'college': "http://happy-dev.fr/owl/#college"
            }
        }

        for kwarg in kwargs:
            if kwarg in ['actor', 'user', 'region', 'college', 'stucturecollege', 'legalrepresentant', 'managementcontact']:
                res.update({kwarg: {'@id': kwargs[kwarg]}})
            else:
                res.update({kwarg: kwargs[kwarg]})

        return res

    # we write functions like this for convenience - we can reuse between tests
    def _get_random_user(self):
        return User.objects.create(
            email='{}@test.co.uk'.format(str(uuid.uuid4())),
            first_name='Test',
            last_name='Test',
            username=str(uuid.uuid4())
        )

    def _get_random_region(self, name='TestRegion'):
        return Region.objects.create(name=name)

    def _get_random_regionalnetwork(self, name='TestRegion'):
        return Regionalnetwork.objects.create(name=name)

    def _get_random_college(self, name='TestCollege'):
        return College.objects.create(name=name)

    def _get_random_paymentmethod(self, name='TestPaymentMethod'):
        return Paymentmethod.objects.create(name=name)

    def _get_random_actor(self, region=None, college=None, another_user=None, shortname='TestActor', longname='TestLongName', owner_user=None):
        if region is None:
            region = self._get_random_region()
        if college is None:
            college = self._get_random_college()
        if another_user is None:
            another_user = self._get_random_user()
        if owner_user is None:
            owner_user = another_user
        return Actor.objects.create(
            shortname=shortname,
            longname=longname,
            region=region,
            college=college,
            adhesiondate='1989',
            legalrepresentant=another_user,
            managementcontact=owner_user
        )

    def _get_random_contribution(self, actor, regionalnetwork, paymentmethod, year=2020):
        return Contribution.objects.create(
            year=year,
            actor=actor,
            paymentto=regionalnetwork,
            paymentmethod=paymentmethod,
            receivedby=regionalnetwork,
            amount=30
        )

    def _get_random_profile(self, user):
        return Profile.objects.create(
            user=user
        )

    def _get_relatedactor(self, user, actor, role='admin'):
        return Relatedactor.objects.create(
            user=user,
            actor=actor,
            role=role
        )

    def _get_random_relatedactor(self):
        actor = self._get_random_actor()
        another_user = self._get_random_user()
        return self._get_relatedactor(actor=actor, user=another_user)

    def _get_random_integrationstep(self):
        actor = self._get_random_actor()
        return Integrationstep.objects.create(actor=actor)

    def _get_random_interventionzone(self, name='TestInterventionzone'):
        return Interventionzone.objects.create(name=name)

    def _get_random_legalstructure(self, name='TestLegalstructure'):
        return Legalstructure.objects.create(name=name)

    def _get_random_collegeepa(self, name='TestCollegeepa'):
        return Collegeepa.objects.create(name=name)

# --- class Region:
    # superadmin : view
    def test_super_user_can_list_region(self):
        self.setUpLoggedInUser(is_superuser=True)
        region = self._get_random_region()

        response = self.client.get('/regions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_post_actor_post_save_signal(self):
        self.setUpLoggedInUser(is_superuser=False)
        region = self._get_random_region()
        zone = self._get_random_interventionzone()
        regional_network = self._get_random_regionalnetwork()
        another_user = self._get_random_user()
        request = {
            "longname":"It's raining again",
            "shortname":"ITR35",
            "location":"",
            "address":"2 Allée de Villebon",
            "postcode":44000,
            "city":"Nantes",
            "lat":47.2226512,
            "lng":-1.5499481,
            "complementaddress":"",
            "region":{"@id": region.urlid},
            "phone":"346758678Y9",
            "adhmail":"",
            "actortype":"soc_citoy",
            "category":"porteur_exploit",
            "legalstructure":"",
            "siren":"",
            "interventionzone":[{"@id": zone.urlid}],
            "adhesiondate":"2019",
            "regionalnetwork":{"@id": regional_network.urlid},
            "numberpeople":"",
            "numberemployees":"",
            "turnover":"",
            "collegeepa":"",
            "college":"",
            "iban":"",
            "logo":"",
            "presentation":"",
            "website":"ww.sfgnfsf.fr",
            "mail":"sympa@sympa.cool",
            "legalrepresentant":{"@id":another_user.urlid},
            "managementcontact":{"@id":another_user.urlid},
            "@context":{"@vocab":"http://happy-dev.fr/owl/#",
                        "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
                        "ldp":"http://www.w3.org/ns/ldp#",
                        "foaf":"http://xmlns.com/foaf/0.1/","name":"rdfs:label","acl":"http://www.w3.org/ns/auth/acl#","permissions":"acl:accessControl","mode":"acl:mode","geo":"http://www.w3.org/2003/01/geo/wgs84_pos#","lat":"geo:lat","lng":"geo:long","subject":"http://happy-dev.fr/owl/#subject"}}

        response = self.client.post('/actors/', data=json.dumps(request), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
        # test effects of signal receiver
        self.assertGreater(Relatedactor.objects.count(), 0)
        self.assertGreater(Contribution.objects.count(), 0)


