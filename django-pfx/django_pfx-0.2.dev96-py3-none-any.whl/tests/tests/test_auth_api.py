import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.test import TransactionTestCase, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import jwt

from pfx.pfxcore.test import APIClient, TestAssertMixin

logger = logging.getLogger(__name__)


class AuthAPITest(TestAssertMixin, TransactionTestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        self.user1 = User.objects.create_user(
            username='jrr.tolkien',
            email="jrr.tolkien@oxford.com",
            password='RIGHT PASSWORD',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
        )

    def test_invalid_login(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'WRONG PASSWORD'})
        self.assertRC(response, 401)

    def test_valid_login(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'RIGHT PASSWORD'})

        self.assertRC(response, 200)
        decoded = jwt.decode(
            response.json_content['token'], settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

    def test_valid_change_password(self):
        self.client.login('jrr.tolkien', 'RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': 'NEW RIGHT PASSWORD'})
        self.assertRC(response, 200)

    def test_invalid_change_password(self):
        self.client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'WRONG PASSWORD',
                'new_password': 'NEW RIGHT PASSWORD'})
        self.assertRC(response, 401)

    @override_settings(PFX_TOKEN_VALIDITY={'minutes': 30})
    def test_valid_token_with_expiration(self):
        self.client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD')

        response = self.client.get(
            '/api/books')
        self.assertRC(response, 200)

    @override_settings(PFX_TOKEN_VALIDITY={'minutes': -30})
    def test_expired_token(self):
        self.client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD')

        response = self.client.get(
            '/api/books')
        self.assertRC(response, 401)

    def test_invalid_token(self):
        token = jwt.encode(
            {'pfx_user_pk': 1}, "A WRONG SECRET", algorithm="HS256")
        logging.disable(logging.CRITICAL)
        response = self.client.get(
            '/api/books',
            HTTP_AUTHORIZATION='Bearer ' + token,
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 401)

    def test_signup(self):
        # Try to create with an existing username
        response = self.client.post(
            '/api/auth/signup', {
                'username': 'jrr.tolkien',
                'email': "jrr.tolkien@oxford.com",
                'first_name': 'John Ronald Reuel',
                'last_name': 'Tolkien',
            })

        self.assertRC(response, 422)
        self.assertEqual(response.json_content['username'],
                         ['A user with that username already exists.'])

        # Then create another valid user
        response = self.client.post(
            '/api/auth/signup', {
                'username': 'isaac.asimov',
                'email': 'isaac.asimov@bu.edu',
                'first_name': 'Isaac',
                'last_name': 'Asimov',
            })

        self.assertRC(response, 200)

    def test_forgotten_password(self):
        # Try with an nonexistent email
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': 'isaac.asimov@bu.edu',
            })

        self.assertRC(response, 404)

        # Then try with an valid email
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': 'jrr.tolkien@oxford.com',
            })

        self.assertRC(response, 200)

    def test_set_password(self):
        # Try with a wrong token and uid
        response = self.client.post(
            '/api/auth/set-password', {
                'token': 'WRONG TOKEN',
                'uidb64': 'WRONG UID',
                'password': 'NEW PASSWORD',
            })

        self.assertRC(response, 401)

        # Then try with an valid token and uid
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
            })
        self.assertRC(response, 200)
