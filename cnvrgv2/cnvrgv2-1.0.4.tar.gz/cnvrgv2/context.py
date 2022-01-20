import os
import requests

from cnvrgv2.config import error_messages, routes
from cnvrgv2.errors import CnvrgError, CnvrgArgumentsError, CnvrgHttpError
from cnvrgv2.config import Config, CONFIG_VERSION
from cnvrgv2.modules.users.users_client import UsersClient
from cnvrgv2.proxy import Proxy, HTTP


class SCOPE:
    PROJECT = {
        "key": "project",
        "dependencies": ["organization", "user"]
    }
    IMAGE = {
        "key": "image",
        "dependencies": ["organization", "user"]
    }
    VOLUME = {
        "key": "volume",
        "dependencies": ["project", "organization", "user"]
    }
    DATASET = {
        "key": "dataset",
        "dependencies": ["organization", "user"]
    }
    COMMIT = {
        "key": "commit",
        "dependencies": ["dataset", "organization", "user"]
    }
    QUERY = {
        "key": "query",
        "dependencies": ["dataset", "organization", "user"]
    }
    RESOURCE = {
        "key": "resource",
        "dependencies": ["organization", "user"]
    }
    TEMPLATE = {
        "key": "template",
        "dependencies": ["resource", "organization", "user"]
    }
    EXPERIMENT = {
        "key": "experiment",
        "dependencies": ["project", "organization", "user"]
    }
    WORKSPACE = {
        "key": "workspace",
        "dependencies": ["project", "organization", "user"]
    }
    WEBAPP = {
        "key": "webapp",
        "dependencies": ["project", "organization", "user"]
    }
    ENDPOINT = {
        "key": "endpoint",
        "dependencies": ["project", "organization", "user"]
    }
    FLOW = {
        "key": "flow",
        "dependencies": ["project", "organization", "user"]
    }
    FLOW_VERSION = {
        "key": "flow-version",
        "dependencies": ["flow", "project", "organization", "user"]
    }
    ORGANIZATION = {
        "key": "organization",
        "dependencies": ["user"]
    }

    @classmethod
    def scopes(cls):
        """
        Calculates all of the scopes from the class attributes
        @return: scope list
        """
        scopes = []
        for attr in dir(cls):
            if not callable(getattr(cls, attr)) and not attr.startswith("__"):
                scopes.append(getattr(cls, attr)["key"])
        return scopes


class Context:
    def __init__(self, context=None, domain=None, user=None, password=None, organization=None, token=None):
        # Set the credentials variables:
        self.token = None
        self.domain = None
        self.user = None

        # Set scope variables:
        for scope in SCOPE.scopes():
            setattr(self, scope, None)

        # If a context is passed, perform a deep copy and return
        if context:
            self._copy_context(context=context, organization=organization)
            return

        # Cannot pass username/password without a domain+username+password or domain + user + token
        if (user or password) and not all([domain, user, password]) and not all([domain, user, token]):
            raise CnvrgArgumentsError(error_messages.CONTEXT_BAD_ARGUMENTS)

        # If a domain is passed, init a blank Cnvrg client
        if domain:
            self.domain = domain

            # Attempt to authenticate using the credentials if they were passed
            if user:
                self._authenticate(domain, user, password, token)
        else:
            self._load_credentials()

        # Override organization if it was explicitly passed
        if organization:
            self.organization = organization

        self.ensure_organization_exist(self.organization)

    def get_scope(self, scope):
        """
        Checks if the current context contains the relevant scope
        @param scope: a SCOPE object constant
        @raise CnvrgError: if the context does not contain the required scope dependencies
        @return: scope dictionary
        """

        dependencies_dict = self._check_dependencies(scope)
        cur_scope = getattr(self, scope["key"], None)
        if cur_scope is None:
            error_msg = error_messages.CONTEXT_SCOPE_BAD_SCOPE.format(scope["key"])
            raise CnvrgError(error_msg)

        return {scope["key"]: cur_scope, **dependencies_dict}

    def set_scope(self, scope, slug):
        """
        Checks if the current context contains the relevant scope and sets new scope
        @param scope: a SCOPE object constant
        @param slug: scope object slug
        @raise CnvrgError: if the context does not contain the required scope dependencies
        @return: slug/None
        """
        if scope == SCOPE.ORGANIZATION:
            self.ensure_organization_exist(slug)

        self._check_dependencies(scope)
        setattr(self, scope["key"], slug)

    def save(self):
        """
        Creates a .cnvrg/config file to reuse authentication.
        Config save will only work in organization context, otherwise an error will be raised
        @raise CnvrgError: Tried to save without having at least organization context
        @return: Boolean depending if context save was successful
        """
        config = Config()
        # Will throw a CnvrgError if organization context is not present
        config_data = self._generate_context_dict()
        config.update(**config_data)

    def _copy_context(self, context, organization=None):
        """
        Performs a deep copy of the supplied context into the current one
        @param context: The source context
        @param organization: Organization name to override
        @return: None
        """
        self.token = context.token
        self.domain = context.domain
        self.user = context.user

        for scope in SCOPE.scopes():
            target_attr = getattr(context, scope, None)
            setattr(self, scope, target_attr)

        if organization:
            self.organization = organization

    def _check_dependencies(self, scope):
        """
        This function checks that the requested scope has all of its dependencies initialized
        @param scope: The scope const we want to check
        @return: dict of scopes and their slugs
        """
        # Build scope object
        scope_dict = {}
        for dependency in scope["dependencies"]:
            dependency_slug = getattr(self, dependency, None)
            if dependency_slug is None:
                error_msg = error_messages.CONTEXT_SCOPE_BAD_DEPENDENCIES.format(scope["key"], dependency)
                raise CnvrgError(error_msg)
            else:
                scope_dict[dependency] = dependency_slug

        return scope_dict

    def _authenticate(self, domain, user, password, user_token=None):
        """
        Performs authentication against Cnvrg and retrieves the auth token
        @param domain: Cnvrg app domain
        @param user: Email with which the user was registered
        @param password: Password with which the user was registered
        @param user_token: user authentication token instead of password
        @return: None
        """
        auth = UsersClient(domain=domain, token=user_token)

        if password is None:
            password = ""

        # Will raise an exception if login did not succeed
        token, organization = auth.login(user=user, password=password)

        if user_token is not None:
            self.token = user_token
        else:
            self.token = token
        self.user = user
        self.organization = organization

        # We don't allow users without an organization to use the context
        if organization is None:
            raise CnvrgError(error_messages.USER_NO_ORGANIZATION)

    def _load_credentials(self):
        """
        Attempts to login using either environment variables or the global Cnvrg config file
        @raise: CnvrgError if cannot login using either method
        @return: None
        """
        logged_in = self._load_from_env() or self._load_from_config()
        if not logged_in:
            raise CnvrgError(error_messages.CONTEXT_BAD_ENV_VARIABLES)

    def _load_from_env(self):
        """
        Attempts to find credentials in environment variables
        @return: Boolean
        """
        token = os.environ.get("CNVRG_JWT_TOKEN", os.environ.get("CNVRG_TOKEN"))
        domain = os.environ.get("CNVRG_URL")
        user = os.environ.get("CNVRG_USER")
        organization = os.environ.get("CNVRG_ORGANIZATION")

        if not all([token, domain, user, organization]):
            return False

        self.token = token
        self.domain = domain
        self.user = user
        self.organization = organization

        # Pod-specific env vars
        project = os.environ.get("CNVRG_PROJECT")
        dataset = os.environ.get("CNVRG_DATASET")

        if project:
            self.project = project
        if dataset:
            self.dataset = dataset

        job_slug = os.environ.get("CNVRG_JOB_ID")
        job_type = os.environ.get("CNVRG_JOB_TYPE")

        if job_type is not None:
            setattr(self, job_type.lower(), job_slug)

        return True

    def _load_from_config(self):
        """
        Attempts to find credentials in local/global config file
        @return: Boolean
        """
        config = Config()
        if not config:
            return False

        token, domain, user = config.get_credential_variables()

        # Context variables
        organization = config.organization

        if not all([token, domain, user, organization]):
            return False

        self.token = token
        self.domain = domain
        self.user = user
        self.organization = organization

        if config.project_slug:
            self.project = config.project_slug
        if config.dataset_slug:
            self.dataset = config.dataset_slug

        return True

    def _generate_context_dict(self):
        """
        Generates a context dict to save in a local config file
        @return: dict
        """
        if not all([self.token, self.domain, self.user, self.organization]):
            raise CnvrgError(error_messages.CONTEXT_CANT_SAVE)

        context = {
            "user": self.user,
            "token": self.token,
            "domain": self.domain,
            "version": CONFIG_VERSION,
            "organization": self.organization,
            "check_certificate": False
        }

        if self.project:
            context["project_slug"] = self.project

        if self.dataset:
            context["dataset_slug"] = self.dataset

        return context

    def ensure_organization_exist(self, name):
        try:
            proxy = Proxy(domain=self.domain, token=self.token)
            organization_route = routes.ORGANIZATION_BASE.format(name)

            proxy.call_api(route=organization_route, http_method=HTTP.GET)

        except CnvrgHttpError as e:
            if e.status_code == requests.codes.not_found:
                raise CnvrgArgumentsError(error_messages.ORGANIZATION_DOESNT_EXIST)
            else:
                # Don't suppress unexpected exceptions
                raise e
