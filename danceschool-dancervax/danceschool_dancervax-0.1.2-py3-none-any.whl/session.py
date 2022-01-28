from django.conf import settings

from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError, InvalidClientError
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import logging

# Define logger for this file
logger = logging.getLogger(__name__)


class DancerVaxSession(object):

    def __init__(self, **kwargs):
        self.client_id = getattr(settings, 'DANCERVAX_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'DANCERVAX_CLIENT_SECRET', None)
        self.token_url = getattr(settings, 'DANCERVAX_TOKEN_URL', 'https://dancervax.org/oauth/token/')
        self.lookup_url = getattr(settings, 'DANCERVAX_LOOKUP_URL', 'https://dancervax.org/api/participants/')

        self.session = None

        if self.client_id:
            self.client = BackendApplicationClient(client_id=self.client_id)
            self.session = OAuth2Session(client=self.client)

    def update_token(self, force=False, verify=True):
        token = self.session.token

        if (
            force or not token or not token.get('expires_at') or
            datetime.fromtimestamp(token.get('expires_at')) > datetime.now() - timedelta(seconds=60)
        ):
            try:
                token = self.session.fetch_token(
                    token_url=self.token_url, client_id=self.client_id,
                    client_secret=self.client_secret, verify=verify,
                )
            except InvalidClientError:
                logger.error('Unable to retrieve an access token from DancerVax. Check credentials in settings.')
                return {}
        return token

    def submit(self, data, **kwargs):
        ''' Wrapper for requeest handling that includes token handling. '''

        token = self.update_token()
        if not token:
            return

        try:
            r = self.session.post(self.lookup_url, json=data, **kwargs)
        except TokenExpiredError as e:
            token = self.update_token(force=True)
            r = self.session.post(self.lookup_url, json=data, **kwargs)

        if not r.ok:
            logger.error('Error accessing data from DancerVax.  Status code {}.'.format(r.status_code))
            return {}

        return r.json()

dancervax_session = DancerVaxSession()