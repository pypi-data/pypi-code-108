import sys
from typing import Optional

from cryptography.x509 import ExtensionOID
from imecilabt_utils import datetime_now
from requests.adapters import HTTPAdapter, DEFAULT_POOLBLOCK
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from urllib3 import Retry
from urllib3.util.ssl_ import create_urllib3_context

import requests
import os
import re

from imecilabt_utils.urn_util import URN

from imecilabt.gpulab.cli.cert_processor import process_cert

GPULAB_LOCALHOST_MODE = 'GPULAB_LOCALHOST_MODE'
GPULAB_API_BASE = 'GPULAB_API_BASE'
JOB_DEFINITION = 'jobDefinition'
GPULAB_API_CLIENT_USER_AGENT_BASE = 'GPULabApiClient/3.1'

# retry with backoff, max 5 retries, resulting in 7.5 seconds backoff time
#  with default timeout ->
# see https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry
GPULAB_CLIENT_RETRIES = Retry(
    total=5,
    read=5,
    connect=5,
    redirect=2,
    status=5,
    backoff_factor=0.25, # backoff_factor * 0 2 4 8 16 32 ... so 0.25 and max 5 => 0.0 0.5 1.0 2.0 4.0 => max 7.5s
    status_forcelist=(500, 502, 504),)


class BadPemPasswordException(Exception):
    pass


class SSLClientCertAdapter(HTTPAdapter):
    def __init__(self, certfile: str, keyfile: str, password: Optional[str] = None,
                 server_self_signed_cert: Optional[str] = None, max_retries: Optional[Retry] = None):
        assert certfile is not None
        assert keyfile is not None
        assert len(keyfile) > 0, "len(keyfile)={} keyfile={}".format(len(keyfile), keyfile)
        assert os.path.isfile(certfile), "certfile '{}' not found".format(certfile)
        assert os.path.isfile(keyfile), "keyfile '{}' not found".format(keyfile)
        self.certfile = certfile
        self.keyfile = keyfile
        self.password = password
        self.server_self_signed_cert = server_self_signed_cert

        super(SSLClientCertAdapter, self).__init__(max_retries=max_retries)

    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
        context = create_urllib3_context()
        try:
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile, password=self.password)
        except FileNotFoundError as e:
            if self.keyfile and self.keyfile != self.certfile:
                print('file not found: certfile="{}" keyfile="{}"'.format(self.certfile, self.keyfile), file=sys.stderr)
            else:
                print('cert file not found: "{}"'.format(self.certfile), file=sys.stderr)
            raise
        except OSError as e:
            # TODO: this works only on linux as the error is system dependent
            if e.errno == 22 and e.strerror == 'Invalid argument':
                raise BadPemPasswordException(e)
            else:
                raise e

        pool_kwargs['ssl_context'] = context
        if self.server_self_signed_cert is not None:
            #ca_certs should work here, but it doesn't
            # print('trusting server certs in '+self.server_self_signed_cert)
            pool_kwargs['ca_certs'] = self.server_self_signed_cert
        # else:
        #     print('only trusting global root certs')

        super(SSLClientCertAdapter, self).init_poolmanager(connections, maxsize, block, **pool_kwargs)


class GpuLabApiClient(object):
    def __init__(self, certfile: str, keyfile: str, password: Optional[str] = None, dev: bool = True,
                 server_self_signed_cert: Optional[str] = None, master_base_url: Optional[str] = None):
        assert certfile is not None
        assert keyfile is not None
        assert len(keyfile) > 0, "len(keyfile)={} keyfile={}".format(len(keyfile), keyfile)
        assert os.path.isfile(certfile), "certfile '{}' not found".format(certfile)
        assert os.path.isfile(keyfile), "keyfile '{}' not found".format(keyfile)

        self.dev = dev
        if master_base_url:
            assert 'api/gpulab/v1.0' not in master_base_url
            assert 'api/gpulab/v2.0' not in master_base_url
            assert 'api/gpulab/v3.0' not in master_base_url
            assert 'gpulab/v' not in master_base_url
            assert master_base_url.endswith('/api/') or master_base_url.endswith('/api')
            self.master_base_url = master_base_url if master_base_url.endswith('/') else master_base_url+'/'
        else:
            self.master_base_url = None

        session = requests.Session()

        #passing server_self_signed_cert should work here, but doesn't,
        # as SSLClientCertAdapter passing ca_certs to init_poolmanager seems not to work
        # (doing it anyway to cover all bases in future versions)
        session.mount(self.get_base_url(),
                      SSLClientCertAdapter(certfile, keyfile, password,
                                           server_self_signed_cert=server_self_signed_cert,
                                           max_retries=GPULAB_CLIENT_RETRIES))

        # passing server_self_signed_cert here does work
        if server_self_signed_cert is not None:
            session.verify = server_self_signed_cert

        from requests.utils import default_user_agent
        # Add user agent with our version, that also refers to python requests
        session.headers.update({'User-Agent': ' '.join([GPULAB_API_CLIENT_USER_AGENT_BASE, default_user_agent()])})
        self.session = session

        cert_info = process_cert(certfile)
        self.user_urn = cert_info.subject_user_urn
        self.username = cert_info.subject_username
        now = datetime_now()
        if cert_info.not_valid_after < now:
            raise ValueError(f'ERROR: The certificate in your login PEM has expired. '
                             f'Try to re-download it from the portal. '
                             f'cert.not_valid_before={cert_info.not_valid_before} '
                             f'cert.not_valid_after={cert_info.not_valid_after} ')
        if cert_info.not_valid_before > now:
            raise ValueError(f'ERROR: The certificate in your login PEM is not yet valid.'
                             f'cert.not_valid_before={cert_info.not_valid_before} '
                             f'cert.not_valid_after={cert_info.not_valid_after} ')

    def get_base_url(self):
        if self.master_base_url:
            return self.master_base_url
        elif GPULAB_LOCALHOST_MODE in os.environ:
            return 'http://localhost:80/api/'
        elif GPULAB_API_BASE in os.environ:
            return os.environ[GPULAB_API_BASE]
        elif self.dev:
            return 'https://dev.gpulab.ilabt.imec.be/api/'
        else:
            return 'https://gpulab.ilabt.imec.be/api/'

    def get_api_url(self, api_version: int):
        master_base_url = self.get_base_url()

        if api_version == 2:
            return master_base_url + 'gpulab/v2.0/'
        elif api_version == 3:
            return master_base_url + 'gpulab/v3.0/'
        else:
            raise ValueError('API version {} not supported'.format(api_version))

    def get_session(self) -> requests.Session:
        """
        :rtype: requests.Session
        :return: a session with the proper client certificate configured
        """
        return self.session


class GpuLabApiLocalhostModeClient(object):
    def __init__(self, local_username: str, fixed_project_urn: str):
        self.dev = False

        session = requests.Session()

        self.username = local_username
        self.user_urn = re.sub(r'\+project\+.*$', '+user+'+local_username, fixed_project_urn)

        #manually add the headers
        session.headers['Fed4fire-Authenticated'] = 'True'
        session.headers['Fed4fire-Authenticated-User-Urn'] = self.user_urn
        session.headers['Fed4Fire-Authenticated-Project-Urns'] = fixed_project_urn

        # Add user agent with our version, that also refers to python requests
        from requests.utils import default_user_agent
        session.headers.update({'User-Agent': ' '.join([GPULAB_API_CLIENT_USER_AGENT_BASE+' (localhost mode)', default_user_agent()])})

        self.session = session

    def get_base_url(self):
        return 'http://localhost:80/api/'

    def get_api_url(self, api_version: int):
        master_base_url = self.get_base_url()

        if api_version == 2:
            return master_base_url + 'gpulab/v2.0/'
        elif api_version == 3:
            return master_base_url + 'gpulab/v3.0/'
        else:
            raise ValueError('API version {} not supported'.format(api_version))

    def get_session(self) -> requests.Session:
        """
        :rtype: requests.Session
        :return: a session with the proper client certificate configured
        """
        return self.session


class GpuLabAnonymousApiClient(object):
    def __init__(self, dev=True, server_self_signed_cert=None, master_base_url=None):
        self.dev = dev

        if master_base_url:
            assert 'api/gpulab/v1.0' not in master_base_url
            assert 'api/gpulab/v2.0' not in master_base_url
            assert 'api/gpulab/v3.0' not in master_base_url
            assert 'gpulab/v' not in master_base_url
            assert master_base_url.endswith('/api/') or master_base_url.endswith('/api')
            self.master_base_url = master_base_url if master_base_url.endswith('/') else master_base_url+'/'
        else:
            self.master_base_url = None

        session = requests.Session()

        # passing server_self_signed_cert here does work
        if server_self_signed_cert is not None:
            session.verify = server_self_signed_cert

        # Add user agent with our version, that also refers to python requests
        from requests.utils import default_user_agent
        session.headers.update({'User-Agent': ' '.join([GPULAB_API_CLIENT_USER_AGENT_BASE+' (anonymous)', default_user_agent()])})

        self.session = session
        self.user_urn = None
        self.username = None

    def get_base_url(self):
        if self.master_base_url:
            return self.master_base_url
        elif GPULAB_LOCALHOST_MODE in os.environ:
            return 'http://localhost:80/api/'
        elif GPULAB_API_BASE in os.environ:
            return os.environ[GPULAB_API_BASE]
        elif self.dev:
            return 'https://dev.gpulab.ilabt.imec.be/api/'
        else:
            return 'https://gpulab.ilabt.imec.be/api/'

    def get_api_url(self, api_version: int):
        master_base_url = self.get_base_url()

        if api_version == 2:
            return master_base_url + 'gpulab/v2.0/'
        elif api_version == 3:
            return master_base_url + 'gpulab/v3.0/'
        else:
            raise ValueError('API version {} not supported'.format(api_version))

    def get_session(self) -> requests.Session:
        """
        :rtype: requests.Session
        :return: a session without any SSL client certificate configured
        """
        return self.session
