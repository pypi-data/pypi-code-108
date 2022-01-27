import fair_research_login
import globus_automate_client
import globus_sdk
import json
import logging.config
import os
import requests
import time
import urllib.request
from .version import __version__ as VERSION
from cfde_submit import CONFIG, exc, globus_http, validation, bdbag_utils
from packaging.version import parse as parse_version

logger = logging.getLogger(__name__)


class CfdeClient:
    """The CfdeClient enables easily using the CFDE tools to ingest data."""
    client_id = "417301b1-5101-456a-8a27-423e71a2ae26"
    config_filename = os.path.expanduser("~/.cfde-submit.cfg")
    app_name = "CfdeClient"
    archive_format = "tgz"

    def __init__(self, tokens=None):
        """Create a CfdeClient.

        Keyword Arguments:
            tokens (dict): A dict keyed by scope, of active Globus Tokens. token keys MUST be a
                    subset of self.scopes. Each token value must contain an additional dict, and
                    have an active "access_token". setting tokens=None will require .login() to
                    be called instead.
                    **Default**: ``None``.
        """
        try:
            with open(self.config_filename) as f:
                config_data = f.readlines()
            if any(x for x in config_data if x.startswith('flows_automated_tests')):
                os.unlink(self.config_filename)
        except FileNotFoundError:
            pass

        self.__service_instance = os.getenv("CFDE_SUBMIT_SERVICE_INSTANCE", "prod")
        self.__remote_config = {}  # managed by property
        self.__tokens = {}
        self.__flow_client = None
        self.__transfer_client = None
        self.transfer_scope = CONFIG["TRANSFER_SCOPE"]
        self.local_config = fair_research_login.ConfigParserTokenStorage(
            filename=self.config_filename
        )
        cli_message = ('Starting login with Globus Auth, '
                       'press ^C twice to cancel or once to manually authenticate')
        code_handlers = [
            fair_research_login.LocalServerCodeHandler(cli_message=cli_message),
            fair_research_login.InputCodeHandler(),
        ]
        self.__native_client = fair_research_login.NativeClient(client_id=self.client_id,
                                                                app_name=self.app_name,
                                                                token_storage=self.local_config,
                                                                code_handlers=code_handlers, )
        self.last_flow_run = {}
        # Fetch dynamic config info
        self.tokens = tokens or {}
        # Set to true when self.check() passes
        self.ready = False

    @property
    def version(self):
        return VERSION

    @property
    def tokens(self):
        if not self.__tokens:
            try:
                self.__tokens = self.__native_client.load_tokens_by_scope(
                    requested_scopes=self.scopes
                )
            except fair_research_login.LoadError:
                raise exc.NotLoggedIn("Client has no tokens, either call login() "
                                      "or supply tokens to client on init.")
        return self.__tokens

    @tokens.setter
    def tokens(self, new_tokens):
        # Check tokens, if supplied outside of client
        if new_tokens and set(new_tokens) != set(self.scopes):
            raise exc.NotLoggedIn("Tokens supplied to CfdeClient are invalid, "
                                  f"They MUST match {self.scopes}")

    @property
    def service_instance(self):
        return self.__service_instance

    @service_instance.setter
    def service_instance(self, new_service_instance):
        valid_si = ["dev", "staging", "prod"]
        if new_service_instance not in valid_si:
            raise exc.CfdeClientException(f"Invalid Service Instance {new_service_instance}, "
                                          f"must be one of {valid_si}")
        self.__service_instance = new_service_instance

    def login(self, **login_kwargs):
        """Login to the cfde-submit client. This will ensure the user has the correct
        tokens configured but it DOES NOT guarantee they are in the correct group to
        run a flow. Can be run both locally and on a server.
        See help(fair_research_login.NativeClient.login) for a full list of kwargs.
        """
        logger.info("Initiating Native App Login...")
        logger.debug(f"Requesting Scopes: {self.scopes}")
        login_kwargs["requested_scopes"] = login_kwargs.get("requested_scopes", self.scopes)
        try:
            self.__native_client.login(**login_kwargs)
        except fair_research_login.LoginException as le:
            raise exc.NotLoggedIn(f"Unable to login: {str(le)}") from le

    def logout(self):
        """Log out and revoke this client's tokens. This object will no longer
        be usable; to submit additional data or check the status of previous submissions,
        you must create a new CfdeClient.
        """
        self.__native_client.logout()

    def is_logged_in(self):
        try:
            return bool(self.tokens)
        except (exc.NotLoggedIn, exc.SubmissionsUnavailable):
            return False

    @property
    def scopes(self):
        return CONFIG["ALL_SCOPES"] + [self.gcs_https_scope, self.flow_scope,
                                       self.transfer_scope]

    @property
    def gcs_https_scope(self):
        remote_ep = self.remote_config["FLOWS"][self.service_instance]["cfde_ep_id"]
        if not remote_ep:
            logger.error(f"Remote Config on {self.service_instance} did not set 'cfde_ep_id'! "
                         f"Dataset submissions cannot be run!")
            raise exc.SubmissionsUnavailable("The remote data server is currently unavailable")
        return f"https://auth.globus.org/scopes/{remote_ep}/https"

    @property
    def flow_scope(self):
        flow_id = self.remote_config["FLOWS"][self.service_instance]["flow_id"]
        if not flow_id:
            logger.error(f"Remote Config on {self.service_instance} did not set 'flow_id'! "
                         f"Dataset submissions cannot be run!")
            raise exc.SubmissionsUnavailable("Submissions have temporarily been disabled, "
                                             "please check with your Administrator.")
        return f"https://auth.globus.org/scopes/{flow_id}/flow_{flow_id.replace('-', '_')}_user"

    @property
    def remote_config(self):
        """Currently there is a problem with GCS not downloading files correctly.
        For now, instead of downloading the config dynamically, we'll just return
        a static config"""
        if self.__remote_config:
            return self.__remote_config
        try:
            dconf_res = requests.get(CONFIG["DYNAMIC_CONFIG_LINKS"][self.service_instance],
                                     headers={"X-Requested-With": "XMLHttpRequest"})
            if dconf_res.status_code >= 300:
                raise ValueError("Unable to download required configuration: Error {}: {}"
                                 .format(dconf_res.status_code, dconf_res.content))
            self.__remote_config = dconf_res.json()
            return self.__remote_config
        except KeyError as e:
            raise ValueError("Flow configuration for service_instance '{}' not found"
                             .format(self.service_instance)) from e
        except json.JSONDecodeError:
            if b"<!DOCTYPE html>" in dconf_res.content:
                raise ValueError("Unable to authenticate with Globus: "
                                 "HTML authentication flow detected")
            else:
                raise ValueError("Flow configuration not JSON: \n{}".format(dconf_res.content))
        except Exception:
            # TODO: Are there other exceptions that need to be handled/translated?
            raise

    @property
    def flow_client(self):
        if self.__flow_client:
            return self.__flow_client
        automate_authorizer = self.__native_client.get_authorizer(
            self.tokens[globus_automate_client.flows_client.MANAGE_FLOWS_SCOPE])
        flow_token = self.tokens[self.flow_scope]['access_token']

        def get_flow_authorizer(*args, **kwargs):
            return globus_sdk.AccessTokenAuthorizer(flow_token)

        self.__flow_client = globus_automate_client.FlowsClient.new_client(
            self.client_id, get_flow_authorizer, automate_authorizer,
        )
        return self.__flow_client

    @property
    def transfer_client(self):
        if self.__transfer_client:
            return self.__transfer_client

        transfer_token = self.tokens[self.transfer_scope]['access_token']
        self.__transfer_client = globus_sdk.TransferClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(transfer_token))
        return self.__transfer_client

    @property
    def https_authorizer(self):
        """Get the https authorizer for downloading/uploading data from the GCS instance.
        This can differ between the dev/staging/prod machines"""
        try:
            return self.__native_client.get_authorizers_by_scope()[self.gcs_https_scope]
        except (fair_research_login.LoadError, KeyError):
            at = self.tokens[self.gcs_https_scope]["access_token"]
            return globus_sdk.AccessTokenAuthorizer(at)

    def _is_json(self, json_string):
        try:
            json.loads(json_string)
        except Exception:
            return False
        return True

    def _format_flow_status(self, data):
        keys_to_ignore = ["creator_id", "manage_by", "monitor_by"]
        result = dict()
        for k, v in data.items():
            if self._is_json(v):
                v = json.loads(v)
            if isinstance(v, dict):
                v = self._format_flow_status(v)
            if v and k not in keys_to_ignore:
                result[k] = v
        return result

    def get_flow_retry_500s(self, flow_id, retries=3, delay=10):
        first_exception = None
        for attempt in range(retries):
            try:
                return self.flow_client.get_flow(flow_id)
            except (globus_sdk.GlobusAPIError, globus_sdk.exc.GlobusAPIError) as e:
                if not first_exception:
                    first_exception = e
                # Retry server errors that may be intermittent
                if 500 <= e.http_status <= 599:
                    time.sleep(delay)
                    continue
                else:
                    raise e
        logger.error(f"Unable to retrieve automate flow after {retries} attempts")
        raise first_exception

    def check(self, raise_exception=True):
        if self.ready:
            return True
        try:
            if not self.tokens:
                logger.debug('No tokens for client, attempting load...')
                self.tokens = self.__native_client.load_tokens_by_scope()
            # Verify client version is compatible with service
            if parse_version(self.remote_config["MIN_VERSION"]) > parse_version(VERSION):
                raise exc.OutdatedVersion(
                    "This CFDE Client is not up to date and can no longer make "
                    "submissions. Please update the client and try again."
                )

            if not self.remote_config["FLOWS"][self.service_instance]["flow_id"]:
                logger.critical(f"Service {self.service_instance} has no flow ID! "
                                f"Submissions will be disabled until that is set!")
                raise exc.SubmissionsUnavailable(
                    "Submissions to nih-cfde.org are temporarily offline. Please check "
                    "with out administrators for further details.")

            # Verify user has permission to view Flow
            try:
                flow_info = self.remote_config["FLOWS"][self.service_instance]
                self.get_flow_retry_500s(flow_info["flow_id"])
            except (globus_sdk.GlobusAPIError, globus_sdk.exc.GlobusAPIError) as e:
                logger.exception(e)
                if e.http_status not in [404, 405]:
                    raise
                error_message = ("Permission denied. Please use the 'Onboarding to the Submission "
                                 "System' page at https://github.com/nih-cfde/published-documentati"
                                 "on/wiki/Onboarding-to-the-CFDE-Portal-Submission-System to "
                                 "change your permissions. Only users with the Submitter role can "
                                 "push data to the submission system. If you have already "
                                 "sent in a request for Submitter status, but are getting this "
                                 "error, be sure that you fully accepted the Globus invitation to "
                                 "your Submitter group. You will need to click the 'Click here to "
                                 "apply for membership' text in the invitation message and follow "
                                 "instructions there before doing a submission.")
                raise exc.PermissionDenied(error_message)

            self.ready = True
            logger.info('Check PASSED, client is ready use flows.')
        except Exception:
            logger.info('Check FAILED, client lacks permissions or is not logged in.')
            self.ready = False
            if raise_exception is True:
                raise

    def start_deriva_flow(self, data_path, dcc_id, catalog_id=None, schema=None, server=None,
                          output_dir=None, delete_dir=False, handle_git_repos=True,
                          dry_run=False, test_sub=False, globus=False, disable_validation=False,
                          **kwargs):
        """Start the Globus Automate Flow to ingest CFDE data into DERIVA.

        Arguments:
            data_path (str): The path to the data to ingest into DERIVA. The path can be:
                    1) A directory to be formatted into a BDBag
                    2) A Git repository to be copied into a BDBag
                    3) A premade BDBag directory
                    4) A premade BDBag in an archive file
            dcc_id (str): The CFDE-recognized DCC ID for this submission.
            catalog_id (int or str): The ID of the DERIVA catalog to ingest into.
                    Default None, to create a new catalog.
            schema (str): The named schema or schema file link to validate data against.
                    Default None, to only validate against the declared TableSchema.
            server (str): The DERIVA server to ingest to.
                    Default None, to use the Action Provider-set default.
            output_dir (str): The path to create an output directory in. The resulting
                    BDBag archive will be named after this directory.
                    If not set, the directory will be turned into a BDBag in-place.
                    For Git repositories, this is automatically set, but can be overridden.
                    If data_path is a file, this has no effect.
                    This dir MUST NOT be in the `data_path` directory or any subdirectories.
                    Default None.
            delete_dir (bool): Should the output_dir be deleted after submission?
                    Has no effect if output_dir is not specified.
                    For Git repositories, this is always True.
                    Default False.
            handle_git_repos (bool): Should Git repositories be detected and handled?
                    When this is False, Git repositories are handled as simple directories
                    instead of Git repositories.
                    Default True.
            dry_run (bool): Should the data be validated and bagged without starting the Flow?
                    When True, does not ingest into DERIVA or start the Globus Automate Flow,
                    and the return value will not have valid DERIVA Flow information.
                    Default False.
            test_sub (bool): Should the submission be run in "test mode" where
                    the submission will be inegsted into DERIVA and immediately deleted?
                    When True, the data wil not remain in DERIVA to be viewed and the
                    Flow will terminate before any curation step.
            globus (bool): Should the data be transferred using Globus Transfer? Default False.

        Other keyword arguments are passed directly to the ``make_bag()`` function of the
        BDBag API (see https://github.com/fair-research/bdbag for details).
        """
        self.check()
        logger.debug("Startup: Validating input")

        catalogs = self.remote_config['CATALOGS']
        if catalog_id in catalogs.keys():
            if schema:
                raise ValueError("You may not specify a schema ('{}') when ingesting to "
                                 "a named catalog ('{}'). Retry without specifying "
                                 "a schema.".format(schema, catalog_id))
            schema = catalogs[catalog_id]

        # Verify the dcc is valid
        if ':' not in dcc_id:
            dcc_id = f"cfde_registry_dcc:{dcc_id}"
        if not self.valid_dcc(dcc_id):
            raise exc.InvalidInput("Error: The dcc you've specified is not valid. Please double "
                                   "check the spelling and try again.")

        # Coerces the BDBag path to a .zip archive
        data_path = bdbag_utils.get_bag(
            data_path, output_dir=output_dir, delete_dir=delete_dir,
            handle_git_repos=handle_git_repos, bdbag_kwargs=kwargs
        )
        # Raises exc.ValidationException if something doesn't match up with the schema
        if not disable_validation:
            validation.validate_user_submission(data_path, schema)

        flow_info = self.remote_config["FLOWS"][self.service_instance]
        dest_path = "{}{}".format(flow_info["cfde_ep_path"], os.path.basename(data_path))

        # If doing dry run, stop here before making Flow input
        if dry_run:
            return {
                "success": True,
                "message": "Dry run validated successfully. No data was transferred."
            }

        logger.debug("Creating input for Flow")
        flow_input = {
            "cfde_ep_id": flow_info["cfde_ep_id"],
            "test_sub": test_sub,
            "dcc_id": dcc_id
        }
        if catalog_id:
            flow_input["catalog_id"] = str(catalog_id)
        if server:
            flow_input["server"] = server

        # Transfer data via globus
        if globus:
            local_endpoint = globus_sdk.LocalGlobusConnectPersonal().endpoint_id
            logger.debug(f'Local endpoint: {local_endpoint}')
            if not local_endpoint:
                raise exc.EndpointUnavailable("Globus Connect Personal installation not found. To "
                                              "install, please visit "
                                              "https://www.globus.org/globus-connect-personal")
            try:
                self.transfer_client.operation_ls(local_endpoint, path=os.path.dirname(data_path))
                logger.debug("Successfully connected to Globus Connect Personal endpoint "
                             f"'{local_endpoint}'")
            except globus_sdk.exc.TransferAPIError as e:

                # Unable to connect
                if e.http_status == 502:
                    raise exc.EndpointUnavailable(f"Unable to connect to local endpoint "
                                                  f"'{local_endpoint}'. Please verify that Globus "
                                                  "Connect Personal is running.")
                # Forbidden
                elif e.http_status == 403:
                    raise exc.EndpointUnavailable(f"Unable to access '{data_path}' on local "
                                                  f"endpoint '{local_endpoint}'. Please set the "
                                                  "access preferences in Globus Connect Personal "
                                                  "to permit access.")

                else:
                    raise exc.EndpointUnavailable(e.message)

            # Populate Transfer fields in Flow
            flow_input.update({
                "source_endpoint_id": local_endpoint,
                "source_path": data_path,
                "cfde_ep_path": dest_path,
                "cfde_ep_url": flow_info["cfde_ep_url"],
                "is_directory": False,
            })

        # Otherwise, HTTP PUT the BDBag on the server
        else:
            logger.debug("Uploading with HTTPS PUT")
            data_url = "{}{}".format(flow_info["cfde_ep_url"], dest_path)
            globus_http.upload(data_path, data_url, self.https_authorizer)
            flow_input.update({
                "source_endpoint_id": False,
                "data_url": data_url,
            })

        logger.debug("Flow input populated:\n{}".format(json.dumps(flow_input, indent=4,
                                                                   sort_keys=True)))
        # Get Flow scope
        flow_id = flow_info["flow_id"]
        # Start Flow
        logger.debug("Starting Flow - Submitting data")
        try:
            flow_res = self.flow_client.run_flow(flow_id, self.flow_scope, flow_input)
        except globus_sdk.GlobusAPIError as e:
            if e.http_status == 404:
                return {
                    "success": False,
                    "error": ("Could not access ingest Flow. Are you in the CFDE DERIVA "
                              "Demo Globus Group? Check your membership or apply for access "
                              "here: https://app.globus.org/groups/a437abe3-c9a4-11e9-b441-"
                              "0efb3ba9a670/about")
                }
            else:
                raise
        self.last_flow_run = {
            "flow_id": flow_id,
            "flow_instance_id": flow_res["action_id"]
        }
        logger.debug("Flow started successfully.")

        return {
            "success": True,
            "message": ("Started DERIVA ingest flow\nYour dataset has been "
                        "submitted\nYou can check the progress with: cfde-submit status\n"),
            "flow_id": flow_id,
            "flow_instance_id": flow_res["action_id"],
            "cfde_dest_path": dest_path,
            "http_link": "{}{}".format(flow_info["cfde_ep_url"], dest_path),
            "globus_web_link": ("https://app.globus.org/file-manager?origin_id={}&origin_path={}"
                                .format(flow_info["cfde_ep_id"], os.path.dirname(dest_path)))
        }

    def check_status(self, flow_id=None, flow_instance_id=None, raw=False):
        """Check the status of a Flow. By default, check the status of the last
        Flow run with this instantiation of the client.

        Arguments:
            flow_id (str): The ID of the Flow run. Default: The last run Flow ID.
            flow_instance_id (str): The ID of the Flow to check.
                    Default: The last Flow instance run with this client.
            raw (bool): Should the status results be returned?
                    Default: False, to print the results instead.
        """
        self.check()
        if not flow_id:
            flow_id = self.last_flow_run.get("flow_id")
        if not flow_instance_id:
            flow_instance_id = self.last_flow_run.get("flow_instance_id")
        if not flow_id or not flow_instance_id:
            raise ValueError("Flow not started and IDs not specified.")

        # Get Flow scope and status
        flow_def = self.flow_client.get_flow(flow_id)
        flow_status = self.flow_client.flow_action_status(flow_id, flow_def["globus_auth_scope"],
                                                          flow_instance_id).data
        flow_info = self.remote_config["FLOWS"][self.service_instance]

        clean_status = ("\nStatus of {} (Flow ID {})\nThis instance ID: {}\n\n"
                        .format(flow_def["title"], flow_id, flow_instance_id))
        # Flow overall status
        # NOTE: Automate Flows do NOT fail automatically if an Action fails.
        #       Any "FAILED" Flow has an error in the Flow itself.
        #       Therefore, "SUCCEEDED" Flows are not guaranteed to have actually succeeded.
        if flow_status["status"] == "ACTIVE":
            clean_status += "This flow is still in progress.\n"
        elif flow_status["status"] == "INACTIVE":
            clean_status += "This flow has stalled, and may need help to resume.\n"
        elif flow_status["status"] == "SUCCEEDED":
            clean_status += "This flow has completed.\n"
        elif flow_status["status"] == "FAILED":
            clean_status += "This flow has failed.\n"

        # Identify error message, if one exists
        try:
            cause = json.loads(flow_status["details"]["details"]["input"]["Cause"])
            error = cause["details"]["error"]
            clean_status += "\n" + error + "\n"
        except KeyError:
            pass

        # Too onerous to pull out results of each step (when even available),
        # also would defeat dynamic config and tie client to Flow.
        # Instead, print out whatever is provided in `details` if Flow FAILED,
        # or print out the appropriate field(s) for the "SUCCEEDED" Flow.
        if flow_status["status"] == "SUCCEEDED":
            flow_output = flow_status["details"]["output"]
            # Each Step is only present in exactly one "SUCCEEDED" Flow result,
            # and they are mutually exclusive
            success_step = flow_info["success_step"]
            failure_step = flow_info["failure_step"]
            error_step = flow_info["error_step"]
            if success_step in flow_output:
                clean_status += flow_output[success_step]["details"]["message"]
            elif failure_step in flow_output:
                clean_status += flow_output[failure_step]["details"]["error"]
            elif error_step in flow_output:
                clean_status += flow_output[error_step]["details"]["error"]
            else:
                clean_status += ("Submission errored: The Flow has finished, but no final "
                                 "details are available.")
            clean_status += "\n"

        elif flow_status["status"] == "FAILED":
            if not error:
                details = flow_status["details"]["details"]
                details_simplified = self._format_flow_status(details)
                clean_status += json.dumps(details_simplified, indent=4, sort_keys=True)

        # Return or print status
        if raw:
            return {
                "success": True,
                "status": flow_status,
                "clean_status": clean_status
            }
        else:
            print(clean_status)

    def valid_dcc(self, dcc):
        """
        Verify that a user specified dcc exists in the deriva registry
        """
        if self.__service_instance == "prod":
            server = "app.nih-cfde.org"
        elif self.__service_instance == "staging":
            server = "app-staging.nih-cfde.org"
        elif self.__service_instance == "dev":
            server = "app-dev.nih-cfde.org"
        url = f"https://{server}/ermrest/catalog/registry/entity/CFDE:dcc"
        with urllib.request.urlopen(url) as page:
            data = json.loads(page.read().decode())
            dccs = [x['id'] for x in data]
        return dcc in dccs
