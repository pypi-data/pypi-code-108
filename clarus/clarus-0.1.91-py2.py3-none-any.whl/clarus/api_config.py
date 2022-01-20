from requests.utils import default_user_agent

import clarus.output_types
import logging
import os

logger = logging.getLogger(__name__)

class ApiConfig(object):
    default_output_type = clarus.output_types.CSV
    resource_path = 'c:/clarusft/data/test/'            # where to look for data files
    key_path      = 'c:/clarusft/keys/'  
    key_file      = 'API-Key.txt'
    secret_file   = 'API-Secret.txt'

    _api_key = None
    _api_secret = None
    _base_url = None
    _base_streaming_url = None
    _user_agent = None
    _client_ticket = None
    _verify = True
    
    _key_init = False
    _secret_init = False
    _base_url_init = False
    _base_streaming_url_init = False
    _user_agent_init = False
    _client_ticket_init = False
        
    def __init__(self):
        pass
    
    @property
    def user_agent(self):
        if (self._user_agent is None and self._user_agent_init == False):
            self._user_agent = " ".join(['%s/%s' % ("clarus.py", 'unknown_version'), #TODO 
                                         default_user_agent()] )
            self._user_agent_init = True
        return self._user_agent
    
    @user_agent.setter
    def user_agent(self, ua):
        self._user_agent = ua
        
    @property
    def client_ticket(self):
        if (self._client_ticket is None and self._client_ticket_init == False):
            self.read_client_ticket()
            self._client_ticket_init = True
        return self._client_ticket
    
    @client_ticket.setter
    def client_ticket(self, ticket):
        self._client_ticket = ticket
        
    def read_client_ticket(self):
        if 'CHARM_CLIENT_TICKET' in os.environ:
            self._client_ticket = os.environ['CHARM_CLIENT_TICKET']
        logger.debug('Client ticket set to {}'.format(self._client_ticket))
            
    @property
    def base_url(self):
        if (self._base_url is None and self._base_url_init == False):
            self.read_base_url()
            self._base_url_init = True
        return self._base_url
    
    @base_url.setter
    def base_url(self, url):
        self._base_url = url
        
    @property
    def ssl_verify(self):
        return self._verify
    
    @ssl_verify.setter
    def ssl_verify(self, verify):
        self._verify = verify
        
    @property
    def base_streaming_url(self):
        if (self._base_streaming_url is None and self._base_streaming_url_init == False):
            self.read_base_streaming_url()
            self._base_streaming_url_init = True
        return self._base_streaming_url
    
    @base_streaming_url.setter
    def base_streaming_url(self, url):
        self._base_streaming_url = url
        
    def read_base_url(self):
        if 'CHARM_API_URL' in os.environ:
            self._base_url = os.environ['CHARM_API_URL']
        if (self._base_url is None):
            self._base_url = 'https://eval.clarusft.com/api/rest/v1/'
        logger.debug('Base URL set to {}'.format(self._base_url))
        
    def read_base_streaming_url(self):
        if 'CHARM_API_STREAMING_URL' in os.environ:
            self._base_streaming_url = os.environ['CHARM_API_STREAMING_URL']
        if (self._base_streaming_url is None):
            self._base_streaming_url = 'wss://eval.clarusft.com/api/ws/v1/'
        logger.debug('Base URL set to {}'.format(self._base_streaming_url))

    @property
    def api_key(self):
        if (self._api_key is None and self._key_init == False):
            self.read_key()
            self._key_init = True
        return self._api_key
    
    @api_key.setter
    def api_key(self, k):
        self._api_key = k
        
    @property
    def api_secret(self):
        if (self._api_secret is None and self._secret_init == False):
            self.read_secret()
            self._secret_init = True
        return self._api_secret
    
    @api_secret.setter
    def api_secret(self, s):
        self._api_secret = s
        
    def read_key(self):
        logger.debug('reading API Key')
        
        self._api_key = self.read_key_file(self.key_file)
        if (self._api_key is None):
            if 'CHARM_API_KEY' in os.environ:
                self._api_key = os.environ['CHARM_API_KEY']
        
        logger.debug('API key set to {}'.format(self._api_key))
    
    def read_secret(self):
        logger.debug('reading API Secret')
        
        self._api_secret = self.read_key_file(self.secret_file)
        if (self._api_secret is None):
            if 'CHARM_API_SECRET' in os.environ:
                self._api_secret = os.environ['CHARM_API_SECRET']
        
        if (self._api_secret is not None and len(self._api_secret) > 40):
            temp_secret_prefix = 'u{}'.format(self.api_key)
            
            if (not self._api_secret.startswith(temp_secret_prefix)):
                self._api_secret = self.kms_decrypt(self._api_secret)
            else:
                logger.debug('temporary secret found')
    
    def read_key_file(self, file):
        if (os.path.isfile(file)) :
            key = open(file).read()
        elif os.path.isdir(self.key_path):
            key = open(self.key_path+file).read()
        else:
            key = None
        return key
    
    def kms_decrypt(self, ciphertext):
        try:
            import boto3
            from base64 import b64decode 
            plaintext = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ciphertext))['Plaintext']
            return plaintext
        except:
            logger.debug('Error decrypting ciphertext')
            return ciphertext
    
ApiConfig = ApiConfig()