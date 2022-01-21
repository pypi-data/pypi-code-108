import requests
from harvest import logger


class Endpoint(object):
    def __init__(self, credential, *args, **kwargs):
        self.credential = credential
        self.path_vars = kwargs

    def get_domain(self):
        return self.domain

    def get_path(self):
        if self.path_vars:
            return self.path.format(**self.path_vars)
        return self.path

    def get_url(self):
        return "{}{}".format(self.get_domain(), self.get_path())

    def get_headers(self):
        return self.headers or {}

    def get(self, *args, **kwargs):
        return self.request("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("post", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request("patch", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request("delete", *args, **kwargs)

    def request(self, http_method, *args, **kwargs):
        verb = http_method
        url = self.get_url()
        params = self.credential.get_params()
        params.update(kwargs.get("params", {}))
        headers = self.credential.get_headers()
        headers.update(kwargs.get("headers", {}))
        data = kwargs.get("data", {})
        logger.debug("HTTP - {} - Request - URL {}".format(verb, url))
        logger.debug("HTTP - {} - Request - Params ".format(verb, params))
        logger.debug("HTTP - {} - Request - Headers {}".format(verb, headers))
        fn = getattr(requests, verb)
        if data:
            resp = fn(url=url, headers=headers, params=params, data=data,)
        else:
            resp = fn(url=url, headers=headers, params=params,)
        logger.debug(
            "HTTP - {} - Response - status code - {}".format(
                verb, resp.status_code
                )
        )
        logger.debug(
            "HTTP - {} - Response - content - {}".format(verb, resp.content)
        )
        return resp


class OAuth2Endpoint(Endpoint):
    domain = "https://id.getharvest.com"


class OAuth2AccessTokenEndpoint(OAuth2Endpoint):
    path = "/api/v2/oauth2/token"

    def post(self, *args, **kwargs):
        if kwargs.get("grant_type") == "refresh_token":
            self.headers.update({"Accept": "application/json"})
        super(OAuth2AccessTokenEndpoint, self).post(*args, **kwargs)


class ApiEndpoint(Endpoint):
    domain = "https://api.harvestapp.com/v2"
    headers = {
        "Accept": "application/json",
    }


class UsersEndpoint(ApiEndpoint):
    path = "/users"


class UsersMeEndpoint(ApiEndpoint):
    path = "/users/me"


class UsersAssignmentsEndpoint(ApiEndpoint):
    path = "/users/{user_id}/project_assignments"


class ProjectsEndpoint(ApiEndpoint):
    path = "/projects"


class TasksEndpoint(ApiEndpoint):
    path = "/tasks"


class TimeEntryEndpoint(ApiEndpoint):
    path = "/time_entries"


class TimeEntryUpdateEndpoint(ApiEndpoint):
    path = "/time_entries/{time_entry_id}"


class TimeEntryStopEndpoint(ApiEndpoint):
    path = "/time_entries/{time_entry_id}/stop"


class TimeEntryRestartEndpoint(ApiEndpoint):
    path = "/time_entries/{time_entry_id}/restart"
