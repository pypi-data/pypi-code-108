import importlib
import re
from logging import getLogger
from typing import List

import urllib3

from rallycli import BaseAPI
from rallycli import SessionBuilder
from rallycli.apis import UserAPI, ArtifactAPI, ProjectAPI, TimeboxAPI, ScmAPI
from rallycli.apis.attdefinition_api import AttdefinitionAPI
from rallycli.errors import RallyError
from rallycli.utils import Timer

## logger definition
logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class RallyAPI(BaseAPI):
    """Client class for accessing Rally Software API.
    Args:
        key_based_auth (bool): True for external key based auth, False BasicAuth.
        external_key (str): Rally generated external API key, stored in ZSESSIONID header parameter.
        username: str = None,
        password: str = None,
        verify_ssl: str = True,
        kwargs (dict):
        Keys:
            baseurl (str): Base url for Rally, default "https://eu1.rallydev.com/"
            proxies (dict):
            Keys:
                http (str): url for http proxy
                https (str): url for https proxy
    """
    ##  PEP 484 type annotations helping for dynamic properties
    user_api: UserAPI
    artifact_api: ArtifactAPI
    project_api: ProjectAPI
    timebox_api: TimeboxAPI
    scm_api: ScmAPI
    attdefinition_api: AttdefinitionAPI

    def __init__(self,
                 key_based_auth: bool = True,
                 external_key: str = None,
                 baseurl: str = None,
                 username: str = None,
                 password: str = None,
                 verify_ssl: bool = True,
                 **kwargs):
        sb = SessionBuilder(key_based_auth,
                            external_key=external_key,
                            username=username,
                            password=password,
                            verify_ssl=verify_ssl,
                            **kwargs)
        rally_session = sb.get_session()
        super().__init__(rally_session,
                         baseurl,
                         str(kwargs.get("workspace")),
                         self)  # Reference to RallyAPI instance for accessing .user_api, .artifact_api ...
        self.key_based_auth: bool = key_based_auth
        if not self.key_based_auth:
            self._set_security_key()
            self._timer = Timer(60)
            self._timer.add(self._set_security_key)
            self._timer.daemon = True
            self._timer.start()
        logger.info("RallyAPI initialized.")

    def __getattr__(self, item):
        """ Intercepts access to properties matching xxxx_api, o xxxx_xxxx_api
        returning instanciated domain class XxxxAPI o XxxxXxxxAPI
        """
        if re.match(r"[a-z].*_api$", item):
            tokens: List[str] = item.split("_")
            u_tokens: List[str] = list(map(lambda t: t.capitalize() if t != "api" else t.upper(), tokens))
            class_name: str = "".join(u_tokens)
            try:
                module = importlib.import_module(f"rallycli.apis.{item}")
                domain_class = getattr(module, class_name)
                return self._get_api_instance(domain_class, item)
            except (ModuleNotFoundError, AttributeError):
                raise RallyError(f"Error trying to access '{self.__class__.__name__}' inner api attribute '{item}':",
                                 f"Module 'rallycli.apis.{item}' with class '{class_name}' not found") \
                    from ModuleNotFoundError
        else:
            return super().__getattribute__(item)
