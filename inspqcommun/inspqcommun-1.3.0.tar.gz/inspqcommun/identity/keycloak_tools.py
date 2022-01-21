import os
import socket
from inspqcommun.identity.keycloak import KeycloakAPI, get_service_account_token, get_token
from distutils.util import strtobool

class KeycloakEnvironment():
    
    def __init__(self,
                 defaultKeycloakPort=18081,
                 defaultAuthClientId="admin-cli",
                 defaultAuthClientSecret = None,
                 defaultProtocol="http",
                 defaultAuthRealm="master",
                 defaultAuthUser='admin',
                 defaultAuthPassword='admin',
                 defaultAdminAuthUser='admin',
                 defaultAdminAuthPassword='admin',
                 defaultAdminAuthRealm='master',
                 defaultValidateCert = False
                 ):
        self.defaultKeycloakPort = defaultKeycloakPort
        self.defaultAuthClientId = defaultAuthClientId
        self.defaultAuthClientSecret = defaultAuthClientSecret
        self.defaultProtocol = defaultProtocol
        self.defaultAuthRealm = defaultAuthRealm
        self.defaultAuthUser = defaultAuthUser
        self.defaultAuthPassword = defaultAuthPassword
        self.defaultAdminAuthUser = defaultAdminAuthUser
        self.defaultAdminAuthPassword = defaultAdminAuthPassword
        self.defaultValidateCert = defaultValidateCert
        self.defaultAdminAuthRealm = defaultAdminAuthRealm
        self.keycloak_enabled = True
        if 'KEYCLOAK_ENABLED' in os.environ:
            self.keycloak_enabled = bool(strtobool(os.environ['KEYCLOAK_ENABLED']))
        if 'KEYCLOAK_BASE_URL' in os.environ:
            self.keycloak_url = "{0}/auth".format(os.environ['KEYCLOAK_BASE_URL'])
        else:
            self.keycloak_url = "{protocol}://{host}:{port}/auth".format(
                protocol=self.defaultProtocol,
                host=socket.getfqdn(),
                port=self.defaultKeycloakPort)
            print("URL Keycloak non specifie: Utilisation de l'URL par defaut")
        self.keycloak_auth_realm = os.environ['KEYCLOAK_AUTH_REALM'] if 'KEYCLOAK_AUTH_REALM' in os.environ else self.defaultAuthRealm
        self.keycloak_auth_client_id = os.environ['KEYCLOAK_AUTH_CLIENT_ID'] if 'KEYCLOAK_AUTH_CLIENT_ID' in os.environ else self.defaultAuthClientId
        self.keycloak_auth_client_secret = os.environ['KEYCLOAK_AUTH_CLIENT_SECRET'] if 'KEYCLOAK_AUTH_CLIENT_SECRET' in os.environ else self.defaultAuthClientSecret
        self.keycloak_auth_user = os.environ['KEYCLOAK_AUTH_USER'] if 'KEYCLOAK_AUTH_USER' in os.environ else self.defaultAuthUser
        self.keycloak_auth_password = os.environ['KEYCLOAK_AUTH_PASSWORD'] if 'KEYCLOAK_AUTH_PASSWORD' in os.environ else self.defaultAuthPassword
        self.keycloak_admin_auth_user = os.environ['KEYCLOAK_ADMIN_AUTH_USER'] if 'KEYCLOAK_ADMIN_AUTH_USER' in os.environ else self.defaultAdminAuthUser
        self.keycloak_admin_auth_password = os.environ['KEYCLOAK_ADMIN_AUTH_PASSWORD'] if 'KEYCLOAK_ADMIN_AUTH_PASSWORD' in os.environ else self.defaultAdminAuthPassword
        self.keycloak_admin_auth_realm = os.environ['KEYCLOAK_ADMIN_AUTH_REALM'] if 'KEYCLOAK_ADMIN_AUTH_REALM' in os.environ else self.defaultAdminAuthRealm
        self.validate_certs = os.environ['VALIDATE_CERTS'] if 'VALIDATE_CERTS' in os.environ else self.defaultValidateCert
        self.kc = self.init_keycloak_api()

    def init_keycloak_api(self):
        if self.keycloak_enabled and self.keycloak_admin_auth_user is not None and self.keycloak_admin_auth_password is not None:
            kcapi = KeycloakAPI(auth_keycloak_url=self.keycloak_url,
                         auth_client_id="admin-cli",
                         auth_username=self.keycloak_admin_auth_user,
                         auth_password=self.keycloak_admin_auth_password,
                         auth_realm=self.keycloak_admin_auth_realm,
                         auth_client_secret=None,
                         validate_certs=self.validate_certs)
        else:
            kcapi = None
        
        return kcapi
        
    def authenticateByServiceAccount(self, client_id=None, client_realm=None):
        headers = {}
        client = client_id if client_id is not None else self.keycloak_auth_client_id
        realm = client_realm if client_realm is not None else self.keycloak_auth_realm

        if self.keycloak_enabled:
            if self.keycloak_auth_client_secret is None and (self.kc is not None or self.init_keycloak_api() is not None):
                self.keycloak_auth_client_secret = self.get_client_secret(client_id=client, realm=realm)
            
            headers = get_service_account_token(
                base_url=self.keycloak_url,
                auth_realm=self.keycloak_auth_realm,
                client_id=client,
                client_secret=self.keycloak_auth_client_secret,
                validate_certs=self.validate_certs) if self.keycloak_auth_client_secret is not None else {}
        self.headers = headers
        return headers

    def authenticateByUsernamePassword(self):
        headers = {}
        if self.keycloak_enabled:
            if self.keycloak_auth_client_secret is None and (self.kc is not None or self.init_keycloak_api() is not None):
                self.keycloak_auth_client_secret = self.get_client_secret(client_id=self.keycloak_auth_client_id, realm=self.keycloak_auth_realm)

            headers = get_token(
                base_url=self.keycloak_url,
                validate_certs=self.validate_certs,
                auth_realm=self.keycloak_auth_realm,
                client_id=self.keycloak_auth_client_id,
                auth_username=self.keycloak_auth_user,
                auth_password=self.keycloak_auth_password, 
                client_secret=self.keycloak_auth_client_secret) if self.keycloak_auth_client_secret is not None else {}
        self.headers = headers
        return headers

    def get_token_url(self):
        token_url = KeycloakAPI.format_token_url(baseurl=self.keycloak_url, realm=self.keycloak_auth_realm)
        return token_url

    def get_client_secret(self, client_id, realm=None):
        if realm is None:
            realm = self.keycloak_auth_realm
        if self.keycloak_enabled and (self.kc is not None or self.init_keycloak_api() is not None):
            keycloak_client = self.kc.get_client_by_clientid(client_id=client_id, realm=realm)
            keycloak_auth_client_secret = self.kc.get_client_secret_by_id(keycloak_client["id"], realm=realm)
            keycloak_auth_client_secret_value = keycloak_auth_client_secret['value'] if keycloak_auth_client_secret is not None and 'value' in keycloak_auth_client_secret else None
            return keycloak_auth_client_secret_value
        return None

        

