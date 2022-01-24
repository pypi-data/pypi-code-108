import json
import logging

from typing import List, Union
from urllib.parse import urljoin

import jwt
import requests

from DKCommon.api_utils.api_utils import validate_and_get_response
from DKCommon.DKFileEncode import DKFileEncode
from DKCommon.DKPathUtils import normalize_list, normalize_recipe_dict, UNIX, WIN
from DKCommon.request_extensions import get_session, get_auth_instance
from DKCommon.request_extensions.settings import DEFAULT_JWT_OPTIONS
from DKCommon.str_utils import decode_bytes
from .DKReturnCode import DKReturnCode, SUCCESS, FAIL

MESSAGE = "message"
DESCRIPTION = "description"
KITCHEN_JSON = "kitchen.json"
LOG = logging.getLogger(__name__)
_DEFAULT_TIMEOUT = 60


class DKApiHelper:
    def __init__(self, base_url, token, **kwargs):
        if not token:
            raise ValueError("Auth token required")
        if not base_url:
            raise ValueError("Url required")

        self._url = base_url
        self._jwt = token
        self._username = kwargs.get("username")
        self._password = kwargs.get("password")
        self.session = get_session()
        self.auth = get_auth_instance(token)
        self._request_timeout = kwargs.get("request_timeout", _DEFAULT_TIMEOUT)

    def __getstate__(self):
        """For security, never actually save password data when pickling."""
        return (self._url, self._jwt, self._username, self._request_timeout)

    def __setstate__(self, state):
        url, token, username, timeout = state
        self._url = url
        self._jwt = token
        self.auth = get_auth_instance(token)
        self._request_timeout = timeout
        self._username = username
        self._password = None
        self.session = get_session()

    def __delete__(self):
        self.session.close()
        super().__delete__()

    @property
    def url(self) -> str:
        return self._url

    @property
    def token(self) -> str:
        return self._jwt

    @classmethod
    def new_from_token(cls, base_url: str, token: str):
        """Create a new instance from a token. Auto-refresh will be unavailable."""
        LOG.debug("%s: creating new session from token", base_url)
        api_helper = cls(base_url, token)
        api_helper.refresh_token()
        return api_helper

    @classmethod
    def new(cls, base_url: str, username: str, password: str):
        endpoint = urljoin(base_url, "v2/login")
        session = get_session()
        LOG.debug("%s: authenticating user %s", endpoint, username)
        with session.post(endpoint, data={"username": username, "password": password}) as r:
            if r.status_code in (200, 201):
                try:
                    token = r.text.strip()
                except AttributeError:
                    try:
                        response = decode_bytes(r.content)
                    except Exception:
                        response = str(r.content)
                    raise Exception(
                        f"Login failed [{endpoint}]: no JWT returned. Response[truncated]: {response[:200]}"
                    )
                try:
                    jwt.decode(token, options=DEFAULT_JWT_OPTIONS)
                except Exception:
                    raise Exception(f"Login failed [{endpoint}]: Login failed; invalid JWT {r.text}")
                else:
                    return cls(base_url, r.text, username=username, password=password)
            else:
                raise Exception(f"Login failed [{endpoint}] ({r.status_code}): {r.text} {r.headers}")

    def refresh_token(self):
        """
        Update and validate the token if necessary.

        The `validatetoken` endpoint will return an update token if the API determined that the token needed to be
        refreshed. If the DKApiHelper class was instanciated with a username and password and the token has expired,
        an attempt to re-authenticate will be made.
        """
        if not self.auth.refreshable:
            return
        if self.auth.expired:
            if self._username and self._password:
                endpoint = f"{self.url}/v2/login"
                with self.session.post(endpoint, data={"username": self._username, "password": self._password}) as r:
                    if r.status_code in (200, 201):
                        try:
                            jwt.decode(r.text, options=DEFAULT_JWT_OPTIONS)
                        except Exception:
                            raise Exception(f"{self._url}: Login failed; invalid JWT {r.text}")
                        else:
                            self._jwt = r.text
                            self.auth = get_auth_instance(r.text)
                            LOG.debug("Token refreshed. New expiration: %s", self.auth.expiration.isoformat())
                            return
                    else:
                        raise Exception(f"{self._url}: Login failed [{r.status_code}]: {r.text} {r.headers}")
            else:
                raise Exception(f"Session for {self._url} has expired.")

        if self.auth.expire_seconds > 180:  # 60 * 3 = 3 minutes
            return

        with self.session.get(f"{self.url}/v2/validatetoken", auth=self.auth) as r:
            if r.status_code == 200:
                new_auth = get_auth_instance(r.json()["token"])
                if new_auth.expiration > self.auth.expiration:
                    self.auth = new_auth
                    self._jwt = r.json()["token"]
                    LOG.debug("Token refreshed. New expiration: %s", new_auth.expiration.isoformat())
                else:
                    LOG.debug("Token validated but server did not provide a newer token.")
            else:
                raise Exception(f"{self.url}: Token validation failed [{r.status_code}]: {r.text}")

    def _set_refreshed_token(self, response):
        """If a response object contained a refreshed_token, set it as the new auth token."""
        token = response.headers.get("refreshed_token")
        if token and self.auth.refreshable:
            try:
                jwt.decode(token, options=DEFAULT_JWT_OPTIONS)
            except Exception:
                LOG.warning("%s: Refresh token was invalid: %s", response.url, token)
                return

            new_auth = get_auth_instance(token)
            if new_auth.expiration > self.auth.expiration:
                self.auth = new_auth
                self._jwt = token

    def _request(self, method: str, endpoint: str, *args, **kwargs):
        self.refresh_token()  # Refresh token if necessary
        kwargs["auth"] = self.auth
        kwargs.setdefault("timeout", self._request_timeout)
        url = urljoin(self._url, endpoint)
        with self.session.request(method, url, *args, **kwargs) as r:
            self._set_refreshed_token(r)
            return r

    def get(self, endpoint: str, *args, **kwargs):
        return self._request("get", endpoint, *args, **kwargs)

    def post(self, endpoint: str, *args, **kwargs):
        return self._request("post", endpoint, *args, **kwargs)

    def put(self, endpoint: str, *args, **kwargs):
        return self._request("put", endpoint, *args, **kwargs)

    def delete(self, endpoint: str, *args, **kwargs):
        return self._request("delete", endpoint, *args, **kwargs)

    def create_order(
        self,
        kitchen,
        recipe_name,
        variation_name,
        node_name=None,
        parameters=None,
        now=False,
        ingredient_owner_order_run=None,
    ):
        """
        Full graph
        '/v2/order/create/<string:kitchenname>/<string:recipename>/<string:variationname>',
            methods=['PUT']

        Single node
        '/v2/order/create/graph/<string:kitchenname>/<string:recipename>/<string:variationname>',
            methods=['PUT']

        """
        if kitchen is None or isinstance(kitchen, str) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        if recipe_name is None or isinstance(recipe_name, str) is False:
            return DKReturnCode(FAIL, "issue with recipe_name")
        if variation_name is None or isinstance(variation_name, str) is False:
            return DKReturnCode(FAIL, "issue with variation_name")

        payload = {"parameters": parameters or {}}

        if now:
            payload["schedule"] = "now"

        if node_name is None:
            endpoint = f"v2/order/create/{kitchen}/{recipe_name}/{variation_name}"
        else:
            endpoint = f"v2/order/create/graph/{kitchen}/{recipe_name}/{variation_name}"
            payload["graph-setting"] = [[node_name]]

        if ingredient_owner_order_run:
            payload["ingredient_owner_order_run"] = ingredient_owner_order_run

        data = json.dumps(payload)

        try:
            response = self.put(endpoint, data=data)
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "create_order: exception: %s" % str(c))
        return DKReturnCode(SUCCESS, None, payload=validate_and_get_response(response))

    def list_kitchen(self):
        try:
            response = self.get("v2/kitchen/list")
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "list_kitchen: exception: %s" % str(c))

        rdict = validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None, payload=rdict["kitchens"])

    def get_kitchen_dict(self, kitchen_name):
        rv = self.list_kitchen()

        kitchens = rv.payload if rv.ok() else None

        if kitchens is None:
            return None

        for kitchen in kitchens:
            if isinstance(kitchen, dict) is True and "name" in kitchen and kitchen_name == kitchen["name"]:
                return kitchen
        return None

    def orderrun_detail(self, kitchen, pdict):
        """
        Get the details about a Order-Run (fka Serving)

        :param kitchen: kitchen name
        :param pdict: parameter dictionary
        :return: DKReturnCode
        """
        if kitchen is None or isinstance(kitchen, str) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        try:
            response = self.post(f"v2/order/details/{kitchen}", data=json.dumps(pdict))
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, f"orderrun_detail: exception: {c}")

        rdict = validate_and_get_response(response)

        return DKReturnCode(SUCCESS, None, payload=rdict)

    def create_kitchen(self, existing_kitchen_name, new_kitchen_name, description, message=None):
        if existing_kitchen_name is None or new_kitchen_name is None:
            return DKReturnCode(FAIL, "Need to supply an existing kitchen name")

        if isinstance(existing_kitchen_name, str) is False or isinstance(new_kitchen_name, str) is False:
            return DKReturnCode(FAIL, "Kitchen name needs to be a string")

        if message is None or isinstance(message, str) is False:
            message = "update_kitchens"

        data = json.dumps({MESSAGE: message, DESCRIPTION: description})
        try:
            response = self.put(f"v2/kitchen/create/{existing_kitchen_name}/{new_kitchen_name}", data=data)
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "create_kitchens: exception: %s" % str(c))

        return DKReturnCode(SUCCESS, None, payload=validate_and_get_response(response))

    def update_kitchen(self, update_kitchen, message):
        if update_kitchen is None:
            return False
        if isinstance(update_kitchen, dict) is False or "name" not in update_kitchen:
            return False
        if message is None or isinstance(message, str) is False:
            message = "update_kitchens"
        data = json.dumps(
            {
                KITCHEN_JSON: update_kitchen,
                MESSAGE: message,
            }
        )
        try:
            response = self.post(f"v2/kitchen/update/{update_kitchen['name']}", data=data)
        except (requests.RequestException, ValueError, TypeError):
            LOG.exception("Error updating kitchen %s", update_kitchen["name"])
            return None
        validate_and_get_response(response)
        return True

    def order_pause(self, kitchen, order_id):
        if kitchen is None or isinstance(kitchen, str) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        if kitchen is None or isinstance(order_id, str) is False:
            return DKReturnCode(FAIL, "issue with order_id")
        try:
            response = self.put(f"v2/order/pause/{order_id}", data=json.dumps({"kitchen_name": kitchen}))
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "order_pause: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def order_unpause(self, kitchen, order_id):
        if kitchen is None or isinstance(kitchen, str) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        if kitchen is None or isinstance(order_id, str) is False:
            return DKReturnCode(FAIL, "issue with order_id")
        try:
            response = self.put(f"v2/order/unpause/{order_id}", data=json.dumps({"kitchen_name": kitchen}))
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "order_unpause: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def order_delete_all(self, kitchen):
        if kitchen is None or isinstance(kitchen, str) is False:
            return DKReturnCode(FAIL, "issue with kitchen")
        try:
            response = self.delete(f"v2/order/deleteall/{kitchen}")
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "order_delete_all: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def orderrun_get_logs(self, kitchen_name, orderrun_id, data):
        if orderrun_id is None or not isinstance(orderrun_id, str):
            return DKReturnCode(FAIL, "issue with orderrun id")
        if kitchen_name is None or not isinstance(kitchen_name, str):
            return DKReturnCode(FAIL, "issue with kitchen name")
        if data is None or not isinstance(data, dict):
            data = {}
        try:
            response = self.get(f"v2/order/logs/{kitchen_name}/{orderrun_id}", data=json.dumps(data))
        except (requests.RequestException, ValueError) as c:
            return DKReturnCode(FAIL, "orderrun_get_logs: exception: %s" % str(c))

        rdict = validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None, payload=rdict)

    def delete_kitchen(self, existing_kitchen_name, message=None, synchronous_delete=False):
        if existing_kitchen_name is None:
            return DKReturnCode(FAIL, "Need to supply an existing kitchen name")

        if isinstance(existing_kitchen_name, str) is False:
            return DKReturnCode(FAIL, "Kitchen name needs to be a string")

        if message is None or isinstance(message, str) is False:
            message = "delete_kitchen"

        data = json.dumps({"synchronous-delete": synchronous_delete, MESSAGE: message})
        try:
            response = self.delete(f"v2/kitchen/delete/{existing_kitchen_name}", data=data)
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "delete_kitchens: exception: %s" % str(c))

        validate_and_get_response(response)
        return DKReturnCode(SUCCESS, None)

    def get_recipe(self, kitchen: str, recipe: str, list_of_files: List[str] = None) -> DKReturnCode:
        if kitchen is None or isinstance(kitchen, str) is False:
            return DKReturnCode(FAIL, "issue with kitchen parameter")

        if recipe is None or isinstance(recipe, str) is False:
            return DKReturnCode(FAIL, "issue with recipe parameter")

        endpoint = f"v2/recipe/get/{kitchen}/{recipe}"
        try:
            if list_of_files is not None:
                params = {"recipe-files": normalize_list(list_of_files, UNIX)}
                response = self.post(endpoint, data=json.dumps(params))
            else:
                response = self.post(endpoint)
        except (requests.RequestException, ValueError, TypeError) as c:
            return DKReturnCode(FAIL, "get_recipe: exception: %s" % str(c))

        rdict = validate_and_get_response(response)
        if recipe not in rdict["recipes"]:
            return DKReturnCode(FAIL, f"Unable to find recipe {recipe} or the stated files within the recipe.")
        else:
            rdict = DKFileEncode.binary_files(DKFileEncode.B64DECODE, rdict)
            return DKReturnCode(SUCCESS, None, payload=normalize_recipe_dict(rdict, WIN))

    # TODO: `headers`, `login`, and `valid_token` are slated for removal. At present they are still used by
    # the CLI utility. When the CLI is updated, these methods may be removed from DKApiHelper

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self._jwt}"}

    @staticmethod
    def login(url, username, password, request_timeout=5):
        session = get_session()
        endpoint = urljoin(url, "v2/login")
        try:
            response = session.post(
                endpoint, data={"username": username, "password": password}, timeout=request_timeout
            )
        except (requests.RequestException, ValueError, TypeError) as c:
            print(f"login: exception: {c}")
            return

        try:
            validate_and_get_response(response)
        except Exception as e:
            print(f"login: exception: {e}")
            return

        if response is not None:
            if response.text is not None and len(response.text) > 10:
                if response.text[0] == '"':
                    return response.text.replace('"', "").strip()

                return response.text
            else:
                print("Invalid jwt token returned from server")
        else:
            print("login: error logging in")

        return None

    @staticmethod
    def valid_token(url: str, token: str, request_timeout=_DEFAULT_TIMEOUT) -> Union[bool, str]:
        session = get_session()
        endpoint = urljoin(url, "v2/validatetoken")
        try:
            response = session.get(endpoint, auth=get_auth_instance(token))
        except Exception:
            LOG.exception("Unable to validate token")
            return False

        try:
            json_response = validate_and_get_response(response)
        except Exception:
            LOG.exception("Unable to validate response from %s", endpoint)
            return False
        try:
            return json_response["token"]
        except KeyError:
            LOG.error("JSON response did not contain token")
            return False
