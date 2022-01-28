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
                'college': "http://happy-dev.fr/owl/#college",
                'admincomment': "http://happy-dev.fr/owl/#admincomment",
                'role': "http://happy-dev.fr/owl/#role"
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

    def _get_random_regionalnetwork(self, name='TestRegionalNetwork'):
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

    def _get_random_integrationstep(self, admincomment='TestAdminComment'):
        return Integrationstep.objects.create(admincomment=admincomment)

    def _get_random_interventionzone(self, name='TestInterventionzone'):
        return Interventionzone.objects.create(name=name)

    def _get_random_legalstructure(self, name='TestLegalstructure'):
        return Legalstructure.objects.create(name=name)

    def _get_random_collegeepa(self, name='TestCollegeepa'):
        return Collegeepa.objects.create(name=name)


    # every function which starts with 'test_' will be ran by the Django test runner as a test (pass, fail, error)
    # pass is great, fail means that our assertion failed and error means that the test itself threw an error
    # we want one test for each behaviour

# --- class Region:
    # superadmin : view
    def test_super_user_can_list_region(self):
        self.setUpLoggedInUser(is_superuser=True)
        region = self._get_random_region()

        response = self.client.get('/regions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # superadmin : change
    def test_super_user_can_modify_region(self):
        self.setUpLoggedInUser(is_superuser=True)
        region = self._get_random_region()

        modified_data = self._get_request_json(name='Occitanie', isocode='FR-OCC')
        response = self.client.patch('/regions/{}/'.format(region.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        region = Region.objects.get(pk=region.pk)
        self.assertEqual(region.name, 'Occitanie')

    # superadmin : add
    def test_super_user_can_post_region(self):
        self.setUpLoggedInUser(is_superuser=True)

        new_data = self._get_request_json(name='Occitanie', isocode='FR-OCC')
        response = self.client.post('/regions/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin or member : view
    def test_admin_or_member_can_list_region(self):
        self.setUpLoggedInUser(is_superuser=False)
        region = self._get_random_region()

        response = self.client.get('/regions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member : change denied
    def test_admin_or_member_cannot_modify_region(self):
        self.setUpLoggedInUser(is_superuser=False)
        region = self._get_random_region()

        modified_data = self._get_request_json(name='Occitanie', isocode='FR-OCC')
        response = self.client.patch('/regions/{}/'.format(region.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member : add denied
    def test_admin_or_member_can_post_region(self):
        self.setUpLoggedInUser(is_superuser=False)

        new_data = self._get_request_json(name='Occitanie', isocode='FR-OCC')
        response = self.client.post('/regions/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)
    

# --- class Regionalnetwork:
    # superadmin : view, add, change
    def test_super_user_can_list_regionalnetwork(self):
        self.setUpLoggedInUser(is_superuser=True)
        regionalnetwork = self._get_random_regionalnetwork()

        response = self.client.get('/regionalnetworks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_super_user_can_modify_regionalnetwork(self):
        self.setUpLoggedInUser(is_superuser=True)
        regionalnetwork = self._get_random_regionalnetwork()

        modified_data = self._get_request_json(name='HD-Occitanie')
        response = self.client.patch('/regionalnetworks/{}/'.format(regionalnetwork.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        regionalnetwork = Regionalnetwork.objects.get(pk=regionalnetwork.pk)
        self.assertEqual(regionalnetwork.name, 'HD-Occitanie')

    def test_super_user_can_post_regionalnetwork(self):
        self.setUpLoggedInUser(is_superuser=True)

        new_data = self._get_request_json(name='HD-Occitanie')
        response = self.client.post('/regionalnetworks/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin or member : view
    def test_admin_or_member_can_list_regionalnetwork(self):
        self.setUpLoggedInUser(is_superuser=False)
        regionalnetwork = self._get_random_regionalnetwork()

        response = self.client.get('/regionalnetworks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member: change denied
    def test_admin_or_member_cannot_change_regionalnetwork(self):
        self.setUpLoggedInUser(is_superuser=False)
        regionalnetwork = self._get_random_regionalnetwork()

        modified_data = self._get_request_json(name='HD-Occitanie')
        response = self.client.patch('/regionalnetworks/{}/'.format(regionalnetwork.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member: add denied
    def test_admin_or_member_cannot_add_regionalnetwork(self):
        self.setUpLoggedInUser(is_superuser=False)

        new_data = self._get_request_json(name='HD-Occitanie')
        response = self.client.post('/regionalnetworks/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_list_regionalnetwork(self):
        regionalnetwork = self._get_random_regionalnetwork()

        response = self.client.get('/regionalnetworks/')
        self.assertEqual(response.status_code, 403)


# --- class Interventionzone:
    # superadmin : view, add, change
    def test_super_user_can_list_interventionzone(self):
        self.setUpLoggedInUser(is_superuser=True)
        interventionzone = self._get_random_interventionzone()

        response = self.client.get('/interventionzones/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_super_user_can_modify_interventionzone(self):
        self.setUpLoggedInUser(is_superuser=True)
        interventionzone = self._get_random_interventionzone()

        modified_data = self._get_request_json(name='NewInterventionzone')
        response = self.client.patch('/interventionzones/{}/'.format(interventionzone.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        interventionzone = Interventionzone.objects.get(pk=interventionzone.pk)
        self.assertEqual(interventionzone.name, 'NewInterventionzone')

    def test_super_user_can_post_interventionzone(self):
        self.setUpLoggedInUser(is_superuser=True)

        new_data = self._get_request_json(name='NewInterventionzone')
        response = self.client.post('/interventionzones/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin or member : view
    def test_admin_or_member_can_list_interventionzone(self):
        self.setUpLoggedInUser(is_superuser=False)
        interventionzone = self._get_random_interventionzone()

        response = self.client.get('/interventionzones/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member: change denied
    def test_admin_or_member_cannot_change_interventionzone(self):
        self.setUpLoggedInUser(is_superuser=False)
        interventionzone = self._get_random_interventionzone()

        modified_data = self._get_request_json(name='NewInterventionzone')
        response = self.client.patch('/interventionzones/{}/'.format(interventionzone.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member: add denied
    def test_admin_or_member_cannot_add_interventionzone(self):
        self.setUpLoggedInUser(is_superuser=False)

        new_data = self._get_request_json(name='NewInterventionzone')
        response = self.client.post('/interventionzones/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_list_interventionzone(self):
        interventionzone = self._get_random_interventionzone()

        response = self.client.get('/interventionzones/')
        self.assertEqual(response.status_code, 403)


# --- class Legalstructure:
    # superadmin : view, add, change
    def test_super_user_can_list_legalstructure(self):
        self.setUpLoggedInUser(is_superuser=True)
        legalstructure = self._get_random_legalstructure()

        response = self.client.get('/legalstructures/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_super_user_can_modify_legalstructure(self):
        self.setUpLoggedInUser(is_superuser=True)
        legalstructure = self._get_random_legalstructure()

        modified_data = self._get_request_json(name='NewLegalstructure')
        response = self.client.patch('/legalstructures/{}/'.format(legalstructure.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        legalstructure = Legalstructure.objects.get(pk=legalstructure.pk)
        self.assertEqual(legalstructure.name, 'NewLegalstructure')

    def test_super_user_can_post_legalstructure(self):
        self.setUpLoggedInUser(is_superuser=True)

        new_data = self._get_request_json(name='NewLegalstructure')
        response = self.client.post('/legalstructures/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin or member : view
    def test_admin_or_member_can_list_legalstructure(self):
        self.setUpLoggedInUser(is_superuser=False)
        legalstructure = self._get_random_legalstructure()

        response = self.client.get('/legalstructures/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member: change denied
    def test_admin_or_member_cannot_change_legalstructure(self):
        self.setUpLoggedInUser(is_superuser=False)
        legalstructure = self._get_random_legalstructure()

        modified_data = self._get_request_json(name='NewLegalstructure')
        response = self.client.patch('/legalstructures/{}/'.format(legalstructure.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member: add denied
    def test_admin_or_member_cannot_add_legalstructure(self):
        self.setUpLoggedInUser(is_superuser=False)

        new_data = self._get_request_json(name='NewLegalstructure')
        response = self.client.post('/legalstructures/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_list_legalstructure(self):
        legalstructure = self._get_random_legalstructure()

        response = self.client.get('/legalstructures/')
        self.assertEqual(response.status_code, 403)


# --- class Collegeepa:
    # superadmin : view, add, change
    def test_super_user_can_list_collegeepa(self):
        self.setUpLoggedInUser(is_superuser=True)
        collegeepa = self._get_random_collegeepa()

        response = self.client.get('/collegeepas/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_super_user_can_modify_collegeepa(self):
        self.setUpLoggedInUser(is_superuser=True)
        collegeepa = self._get_random_collegeepa()

        modified_data = self._get_request_json(name='NewCollegeepa')
        response = self.client.patch('/collegeepas/{}/'.format(collegeepa.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        collegeepa = Collegeepa.objects.get(pk=collegeepa.pk)
        self.assertEqual(collegeepa.name, 'NewCollegeepa')

    def test_super_user_can_post_collegeepa(self):
        self.setUpLoggedInUser(is_superuser=True)

        new_data = self._get_request_json(name='NewCollegeepa')
        response = self.client.post('/collegeepas/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin or member : view
    def test_admin_or_member_can_list_collegeepa(self):
        self.setUpLoggedInUser(is_superuser=False)
        collegeepa = self._get_random_collegeepa()

        response = self.client.get('/collegeepas/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member: change denied
    def test_admin_or_member_cannot_change_collegeepa(self):
        self.setUpLoggedInUser(is_superuser=False)
        collegeepa = self._get_random_collegeepa()

        modified_data = self._get_request_json(name='NewCollegeepa')
        response = self.client.patch('/collegeepas/{}/'.format(collegeepa.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member: add denied
    def test_admin_or_member_cannot_add_collegeepa(self):
        self.setUpLoggedInUser(is_superuser=False)

        new_data = self._get_request_json(name='NewCollegeepa')
        response = self.client.post('/collegeepas/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_list_collegeepa(self):
        collegeepa = self._get_random_collegeepa()

        response = self.client.get('/collegeepas/')
        self.assertEqual(response.status_code, 403)


# --- class College:
    # superadmin : view, add, change
    def test_super_user_can_list_college(self):
        self.setUpLoggedInUser(is_superuser=True)
        college = self._get_random_college()

        response = self.client.get('/colleges/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_super_user_can_modify_college(self):
        self.setUpLoggedInUser(is_superuser=True)
        college = self._get_random_college()

        modified_data = self._get_request_json(name='NewCollege')
        response = self.client.patch('/colleges/{}/'.format(college.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        college = College.objects.get(pk=college.pk)
        self.assertEqual(college.name, 'NewCollege')

    def test_super_user_can_post_college(self):
        self.setUpLoggedInUser(is_superuser=True)

        new_data = self._get_request_json(name='NewCollege')
        response = self.client.post('/colleges/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin or member : view
    def test_admin_or_member_can_list_college(self):
        self.setUpLoggedInUser(is_superuser=False)
        college = self._get_random_college()

        response = self.client.get('/colleges/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member: change denied
    def test_admin_or_member_cannot_change_college(self):
        self.setUpLoggedInUser(is_superuser=False)
        college = self._get_random_college()

        modified_data = self._get_request_json(name='NewCollege')
        response = self.client.patch('/colleges/{}/'.format(college.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member: add denied
    def test_admin_or_member_cannot_add_college(self):
        self.setUpLoggedInUser(is_superuser=False)

        new_data = self._get_request_json(name='NewCollege')
        response = self.client.post('/colleges/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_list_college(self):
        college = self._get_random_college()

        response = self.client.get('/colleges/')
        self.assertEqual(response.status_code, 403)

# --- class Paymentmethod:
    # superadmin : view, add, change
    def test_super_user_can_list_paymentmethod(self):
        self.setUpLoggedInUser(is_superuser=True)
        paymentmethod = self._get_random_paymentmethod()

        response = self.client.get('/paymentmethods/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_super_user_can_modify_paymentmethod(self):
        self.setUpLoggedInUser(is_superuser=True)
        paymentmethod = self._get_random_paymentmethod()

        modified_data = self._get_request_json(name='NewPaymentmethod')
        response = self.client.patch('/paymentmethods/{}/'.format(paymentmethod.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        paymentmethod = Paymentmethod.objects.get(pk=paymentmethod.pk)
        self.assertEqual(paymentmethod.name, 'NewPaymentmethod')

    def test_super_user_can_post_paymentmethod(self):
        self.setUpLoggedInUser(is_superuser=True)

        region = self._get_random_region()
        new_data = self._get_request_json(name='NewPaymentmethod')
        response = self.client.post('/paymentmethods/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin or member : view
    def test_admin_or_member_can_list_paymentmethod(self):
        self.setUpLoggedInUser(is_superuser=False)
        paymentmethod = self._get_random_paymentmethod()

        response = self.client.get('/paymentmethods/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member: change denied
    def test_admin_or_member_cannot_change_paymentmethod(self):
        self.setUpLoggedInUser(is_superuser=False)
        paymentmethod = self._get_random_paymentmethod()

        modified_data = self._get_request_json(name='NewPaymentmethod')
        response = self.client.patch('/paymentmethods/{}/'.format(paymentmethod.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member: add denied
    def test_admin_or_member_cannot_add_paymentmethod(self):
        self.setUpLoggedInUser(is_superuser=False)

        new_data = self._get_request_json(name='NewPaymentmethod')
        response = self.client.post('/paymentmethods/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_list_paymentmethod(self):
        paymentmethod = self._get_random_paymentmethod()

        response = self.client.get('/paymentmethods/')
        self.assertEqual(response.status_code, 403)


# --- class Profile ---
    # superadmin : view
    def test_super_user_can_list_profile(self):
        self.setUpLoggedInUser(is_superuser=True)
        another_user = self._get_random_user()

        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['ldp:contains']), 2)

    # superadmin : change
    def test_super_user_can_change_profile(self):
        self.setUpLoggedInUser(is_superuser=True)
        another_user = self._get_random_user()
        another_profile = Profile.objects.get(user=another_user)

        modified_data = self._get_request_json(presentation='Hello')
        response = self.client.patch('/profiles/{}/'.format(another_profile.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        another_profile = Profile.objects.get(pk=another_profile.pk)
        self.assertEqual(another_profile.presentation, 'Hello')  

#    # superadmin : add
#    def test_super_user_can_add_profile(self):
#        self.setUpLoggedInUser(is_superuser=True)
#        another_user = self._get_random_user()
#
#        new_data = self._get_request_json(user=another_user.urlid)
#        response = self.client.post('/profiles/', json.dumps(new_data), content_type='application/ld+json')
#        self.assertEqual(response.status_code, 201)

    # admin or member : view only his own
    def test_user_can_list_only_its_profile(self):
        self.setUpLoggedInUser(is_superuser=False)
        ownprofile = Profile.objects.get(user=self.user)
        another_user = self._get_random_user()
        another_profile = Profile.objects.get(user=another_user)

        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # admin or member : change only his own
    def test_user_can_change_only_its_profile(self):
        self.setUpLoggedInUser(is_superuser=False)
        ownprofile = Profile.objects.get(user=self.user)
        another_user = self._get_random_user()
        another_profile = Profile.objects.get(user=another_user)

        modified_data = self._get_request_json(presentation='Hello')
        response = self.client.patch('/profiles/{}/'.format(ownprofile.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        response = self.client.patch('/profiles/{}/'.format(another_profile.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

        ownprofile = Profile.objects.get(pk=ownprofile.pk)
        self.assertEqual(ownprofile.presentation, 'Hello')       
        another_profile = Profile.objects.get(pk=another_profile.pk)
        self.assertEqual(another_profile.presentation, None)

# --- class Actor ---
    # superadmin : view
    def test_super_user_can_list_actor(self):
        self.setUpLoggedInUser(is_superuser=True)
        self._get_random_actor()

        response = self.client.get('/actors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # superadmin : change
    def test_super_user_can_change_actor(self):
        self.setUpLoggedInUser(is_superuser=True)
        actor = self._get_random_actor()

        modified_data = self._get_request_json(postcode='33800')
        response = self.client.patch('/actors/{}/'.format(actor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        another_profile = Actor.objects.get(pk=actor.pk)
        self.assertEqual(another_profile.postcode, '33800')  

    # superadmin : add
    def test_super_user_can_add_actor(self):
        self.setUpLoggedInUser(is_superuser=True)

        region = self._get_random_region()
        college = self._get_random_college()
        another_user = self._get_random_user()
        new_data = self._get_request_json(
            region=region.urlid, 
            college=college.urlid, 
            legalrepresentant=another_user.urlid,
            managementcontact=another_user.urlid,
            shortname='James',
            longname='Bond',
            adhesiondate='1968',
            mail='jamesbond@mi6.uk',
            adhmail='jamesbond@mi6.uk',
            address='London'
            )
        response = self.client.post('/actors/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # admin : view
    def test_admin_can_list_all_actor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()
        relatedactor = self._get_relatedactor(self.user, self.actor, 'admin')
        
        another_actor = self._get_random_actor()
        another_user = self._get_random_user()
        another_relatedactor = self._get_relatedactor(another_user, another_actor, 'admin')

        response = self.client.get('/actors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 2)

    # admin : change own
    def test_admin_can_change_own_actor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor(self.user)

        modified_data = self._get_request_json(postcode='33800')
        response = self.client.patch('/actors/{}/'.format(self.actor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        another_profile = Actor.objects.get(pk=self.actor.pk)
        self.assertEqual(another_profile.postcode, '33800')  

    def test_admin_cannot_change_other_actor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()

        modified_data = self._get_request_json(postcode='33800')
        response = self.client.patch('/actors/{}/'.format(self.actor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # member : view own
    def test_member_can_list_all_actor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()
        relatedactor = self._get_relatedactor(self.user, self.actor, 'member')

        another_actor = self._get_random_actor()
        another_user = self._get_random_user()
        another_relatedactor = self._get_relatedactor(another_user, another_actor, 'member')

        response = self.client.get('/actors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 2)

    # member : change denied
    def test_member_cannot_change_own_actor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()
        relatedactor = self._get_relatedactor(self.user, self.actor, 'member')

        modified_data = self._get_request_json(postcode='33800')
        response = self.client.patch('/actors/{}/'.format(self.actor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403) 

    def test_member_cannot_change_other_actor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()

        modified_data = self._get_request_json(postcode='33800')
        response = self.client.patch('/actors/{}/'.format(self.actor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # admin or member : add
    def test_admin_can_add_actor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()

        region = self._get_random_region()
        college = self._get_random_college()
        another_user = self._get_random_user()
        new_data = self._get_request_json(
            region=region.urlid, 
            college=college.urlid, 
            legalrepresentant=another_user.urlid,
            managementcontact=another_user.urlid,
            shortname='James',
            longname='Bond',
            adhesiondate='1968',
            mail='jamesbond@mi6.uk',
            adhmail='jamesbond@mi6.uk',
            address='London'
            )
        response = self.client.post('/actors/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

# --- class Integrationstep  ---
    # superadmin : view
    def test_super_user_can_list_integrationstep(self):
        self.setUpLoggedInUser(is_superuser=True)
        integrationstep = self._get_random_integrationstep()

        response = self.client.get('/integrationsteps/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # superadmin : add
    def test_super_user_can_add_integrationstep(self):
        self.setUpLoggedInUser(is_superuser=True)
        actor = self._get_random_actor()

        new_data = self._get_request_json(admincomment='New comment')
        response = self.client.post('/integrationsteps/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # superadmin : change
    def test_super_user_can_change_integrationstep(self):
        self.setUpLoggedInUser(is_superuser=True)
        integrationstep = self._get_random_integrationstep()

        modified_data = self._get_request_json(admincomment='New comment')
        response = self.client.patch('/integrationsteps/{}/'.format(integrationstep.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        integrationstep = Integrationstep.objects.get(pk=integrationstep.pk)
        self.assertEqual(integrationstep.admincomment, 'New comment')   

    # member or admin : view denied
    def test_member_or_admin_cannot_list_integrationstep(self):
        self.setUpLoggedInUser(is_superuser=False)
        integrationstep = self._get_random_integrationstep()

        response = self.client.get('/integrationsteps/{}/'.format(integrationstep.pk))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_list_integrationstep(self):
        integrationstep = self._get_random_integrationstep()

        response = self.client.get('/integrationsteps/{}/'.format(integrationstep.pk))
        self.assertEqual(response.status_code, 404)


# --- class Contribution ---
    # superadmin : view
    def test_super_user_can_list_contribution(self):
        self.setUpLoggedInUser(is_superuser=True)
        self.setUpActor()
        # self.setUpContribution()

        response = self.client.get('/contributions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # superadmin : add
    def test_super_user_can_add_contribution(self):
        self.setUpLoggedInUser(is_superuser=True)
        self.setUpActor()

        new_data = self._get_request_json(year=2021,amount=43, actor=self.actor.urlid)
        response = self.client.post('/contributions/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # superadmin : change
    def test_super_user_can_change_contribution(self):
        self.setUpLoggedInUser(is_superuser=True)
        self.setUpActor()
        self.setUpContribution()

        modified_data = self._get_request_json(year=2021,amount=43)
        response = self.client.patch('/contributions/{}/'.format(self.contribution.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        contribution = Contribution.objects.get(pk=self.contribution.pk)
        self.assertEqual(contribution.year, 2021)

    # admin : view his own
    def test_admin_can_list_own_contribution(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor(self.user)

        self._get_random_actor()

        response = self.client.get('/contributions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contribution.objects.count(), 2)
        self.assertEqual(len(response.data['ldp:contains']), 1)


    # admin : view his own nested in actor
    def test_admin_can_list_own_nested_contribution(self):
        self.setUpLoggedInUser(is_superuser=False)

        another_actor = self._get_random_actor()
        another_user = self._get_random_user()
        another_relatedactor = self._get_relatedactor(actor = another_actor, user = another_user, role = 'member')

        self.setUpActor(self.user)

        response = self.client.get('/actors/{}/contributions/'.format(self.actor.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

        a_third_actor = self._get_random_actor()

        response = self.client.get('/actors/{}/contributions/'.format(a_third_actor.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)
    
    # member: view denied
    def test_member_cannot_list_contributions(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()
        self.setUpContribution()
        relatedactor = self._get_relatedactor(self.user, self.actor, 'member')

        response = self.client.get('/contributions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

    # admin or member : add denied   
    def test_non_super_user_cannot_change_contribution(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()
        self.setUpContribution()
        
        modified_data = self._get_request_json(year=2021,amount=43)
        response = self.client.patch('/contributions/{}/'.format(self.contribution.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin or member : add denied
    def test_non_super_user_cannot_add_contribution(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()
        relatedactor = self._get_relatedactor(self.user, self.actor, 'member')

        new_data = self._get_request_json(year=2021,amount=43, actor=self.actor.urlid)
        response = self.client.post('/contributions/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)   


# --- class RelatedActor
    # superadmin: view
    def test_super_user_can_list_relatedactor(self):
        self.setUpLoggedInUser(is_superuser=True)
        # since creating an actor creates the relatedactor associated
        actor = self._get_random_actor()

        response = self.client.get('/relatedactors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # superadmin: add
    def test_super_user_can_add_relatedactor(self):
        self.setUpLoggedInUser(is_superuser=True)
        user = self._get_random_user()
        actor = self._get_random_actor()

        new_data = self._get_request_json(
            user=user.urlid,
            actor=actor.urlid
            )
        response = self.client.post('/relatedactors/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # superadmin: change
    def test_super_user_can_change_relatedactor(self):
        self.setUpLoggedInUser(is_superuser=True)
        relatedactor = self._get_random_relatedactor()
        another_actor = self._get_random_actor()

        modified_data = self._get_request_json(actor=another_actor.urlid)
        response = self.client.patch('/relatedactors/{}/'.format(relatedactor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        relatedactor = Relatedactor.objects.get(pk=relatedactor.pk)
        self.assertEqual(relatedactor.actor, another_actor)         

    # admin: view relatedactors of its actor
    def test_admin_can_list_only_its_actor_relatedactors(self):
        # NB: creating an actor creates a relatedactor with the owner as admin
        # Actor and relatedactor with user as admin
        self.setUpLoggedInUser(is_superuser=False)       
        actor = self._get_random_actor(owner_user=self.user)
        
        # Another relatedactor to the actor the self.user is admin
        another_user = self._get_random_user()
        a_relatedactor_related_to_the_actor = self._get_relatedactor(actor=actor, user=another_user, role='member')

        # An unrelated actor
        another_actor = self._get_random_actor()

        # 3 relatedactors are created but member can see only 2
        self.assertEqual(len(Relatedactor.objects.all()), 3)
        response = self.client.get('/relatedactors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 2)

    # admin: change relatedactors of its actor
    def test_admin_can_change_its_actor_relatedactors(self):
        self.setUpLoggedInUser(is_superuser=False)       
        actor = self._get_random_actor(owner_user=self.user)

        another_user = self._get_random_user()
        another_relatedactor = self._get_relatedactor(actor=actor, user=another_user, role='member')

        modified_data = self._get_request_json(role='admin')
        response = self.client.patch('/relatedactors/{}/'.format(another_relatedactor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)


        relatedactor = Relatedactor.objects.get(pk=another_relatedactor.pk)
        self.assertEqual(relatedactor.role, 'admin')  
        
    def test_admin_cannot_change_another_relatedactor(self):
        self.setUpLoggedInUser(is_superuser=False)
        actor = self._get_random_actor()
        another_user = self._get_random_user()
        relatedactor = self._get_relatedactor(user=another_user, actor=actor, role='admin')

        another_actor = self._get_random_actor()
        modified_data = self._get_request_json(actor=another_actor.urlid)
        response = self.client.patch('/relatedactors/{}/'.format(relatedactor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # admin: add
    def test_admin_can_add_relatedactor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()

        self._get_relatedactor(actor=self.actor, user=self.user, role='admin')

        another_user = self._get_random_user()

        new_data = self._get_request_json(
            user=another_user.urlid,
            actor=self.actor.urlid
        )
        response = self.client.post('/relatedactors/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # member: view relatedactors of its actor
    def test_member_can_list_only_its_relatedactor(self):
        # NB: creating an actor creates a relatedactor with the owner as admin
        # Actor and relatedactor with user as member
        self.setUpLoggedInUser(is_superuser=False)
        actor = self._get_random_actor()
        relatedactor = self._get_relatedactor(user=self.user, actor=actor, role='member')

        # Another relatedactor to the actor the self.user is member
        another_user = self._get_random_user()
        a_relatedactor_related_to_the_actor = self._get_relatedactor(actor=actor, user=another_user, role='member')

        # An unrelated actor
        another_actor = self._get_random_actor()

        # 4 relatedactors are created but member can see only 3
        self.assertEqual(len(Relatedactor.objects.all()), 4)
        response = self.client.get('/relatedactors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 3)

    # member: change denied
    def test_member_cannot_change_another_relatedactor(self):
        self.setUpLoggedInUser(is_superuser=False)
        actor = self._get_random_actor()
        relatedactor = self._get_relatedactor(user=self.user, actor=actor, role='member')

        another_actor = self._get_random_actor()
        modified_data = self._get_request_json(actor=another_actor.urlid)
        response = self.client.patch('/relatedactors/{}/'.format(relatedactor.pk), json.dumps(modified_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # member: add
    def test_member_can_add_relatedactor(self):
        self.setUpLoggedInUser(is_superuser=False)
        self.setUpActor()

        self._get_relatedactor(actor=self.actor, user=self.user, role='member')

        another_user = self._get_random_user()

        new_data = self._get_request_json(
            user=another_user.urlid,
            actor=self.actor.urlid
        )
        response = self.client.post('/relatedactors/', json.dumps(new_data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # authenticated: can add with an empty role 
    def test_authenticated_user_can_add_relatedactor_with_empty_role(self):
        self.setUpLoggedInUser(is_superuser=False)
        actor = self._get_random_actor()
 
        new_data = self._get_request_json(
            user=self.user.urlid,
            actor=actor.urlid
            )
        response = self.client.post('/relatedactors/', json.dumps(new_data), content_type='application/ld+json')
        
        self.assertEqual(response.status_code, 201)
 
    # authenticated: cannot add with a defined role 
    def test_authenticated_user_can_add_relatedactor_with_defined_role(self):
        self.setUpLoggedInUser(is_superuser=False)
        actor = self._get_random_actor()

        new_data = self._get_request_json(
            user=self.user.urlid,
            actor=actor.urlid,
            role='admin'
            )
        response = self.client.post('/relatedactors/', json.dumps(new_data), content_type='application/ld+json')
        
        self.assertEqual(response.status_code, 403)