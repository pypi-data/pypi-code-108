from django.conf import settings
from psu_base.classes.Log import Log
from psu_base.classes.Faki import Faki
from psu_base.services import (
    message_service,
    utility_service,
    error_service,
    validation_service,
)
import requests
import json

log = Log()


class Finti:
    # Configurable properties:
    content_type = {"Content-Type": "application/json"}
    reduce_logging = False  # Reduce log clutter
    suppress_logging = False  # Do not log (sensitive data)

    # Status indicators
    successful = None
    error_message = None
    http_status_code = None

    # Automatically configured based on settings:
    token = None
    finti_url = None
    auth = None
    verify_certificate = True

    # For caching finti responses for offline development
    # This should only be used for local development
    faki = None
    simulate = None
    simulate_when_possible = None
    prepare_offline = None

    @staticmethod
    def encode_special_chars(
        content, limit_special_chars=True, limit_name_characters=False
    ):
        """
        Passing special chars through Finti does not work.  Rather, convert to character codes
        and then decode them in Oracle.  This function just returns an encoded string to pass to Oracle.

        limit_special_chars=True will remove or replace characters not allowed in Banner

        Note: The dbproc must be expecting this encoded content
        """
        if content:
            if limit_name_characters:
                content, changed = validation_service.clean_name(content)
                if changed:
                    log.warning("Content's special-characters have been altered.")
            elif limit_special_chars:
                content, changed = validation_service.clean_special_characters(content)
                if changed:
                    log.warning("Content's special-characters have been altered.")
            content = str([ord(c) for c in content]).strip("[]").replace(" ", "")
        return content

    def finalize_response(self, data, include_metadata):
        self.successful = None
        self.http_status_code = None
        self.error_message = None

        # Get just the "message" if present
        message = data["message"] if type(data) is dict and "message" in data else data

        # Check for success/failure
        if type(data) is dict:
            if "result" in data:
                self.successful = data["result"] == "success"
            elif "status" in data:
                self.successful = data["status"] == "200"

        # Set http status code
        if data and "status" in data and str(data["status"]).isnumeric():
            self.http_status_code = int(data["status"])
        elif self.successful:
            self.http_status_code = 200
        elif self.successful is not None and not self.successful:
            self.http_status_code = 400
        else:
            # Since success could not be determined (non-standard Finti response), mark as
            # a successful (200) response and the app will have to determine if the message is as expected
            self.http_status_code = 200

        # If not successful
        if self.successful is not None and not self.successful:
            self.error_message = message
            if self.can_log():
                if "<!DOCTYPE html>" in str(data):
                    log.error(
                        f"Finti returned an HTML page ({self.http_status_code})",
                        trace_error=False,
                    )
                else:
                    log.error(data, trace_error=False)

        # If success could not be determined
        elif self.successful is None and self.max_logging():
            log.warning(f"Non-standard response: {data}")

        # If not reducing log messages
        elif self.max_logging():
            if message and len(str(message)) > 100:
                log.info(f"Finti Response: {str(message)[0:99]}...")
            else:
                log.info(f"Finti Response: {message}")

        return data if include_metadata else message

    # Calls with regular/registered Finti tokens
    def get(self, path, parameters=None, include_metadata=False):
        """
        Get a response from Finti
        :param path:             Finti path relative to root Finti URL
        :param parameters:       Object (map) of parameters to send to Finti
        :param include_metadata: Include status, version, result, jwt?              (default: False)
        """

        # Special characters cannot be sent through Finti and result in unhandled exceptions
        # Remove any special characters that have not been encoded via Finti.encode_special_chars()
        if parameters:
            try:
                for kk, vv in parameters.items():
                    (
                        parameters[kk],
                        changed,
                    ) = validation_service.remove_special_characters(vv)
                    if changed:
                        log.warning(
                            f"Parameter {kk}'s special-characters have been altered."
                        )
            except Exception as ee:
                error_service.record(
                    ee, "Removing special characters from Finti parameters"
                )

        params = {"path": path, "parameters": parameters}
        if self.can_log():
            log.trace(params)

        json_response = None

        # If simulating responses, or preparing to simulate them in the future, prepare a Faki instance
        if self.simulate or self.prepare_offline or self.simulate_when_possible:
            self.faki = Faki(
                path, method="GET", parameters=parameters, payload=None, headers=None
            )

        # If getting offline data
        simulated = False
        if self.simulate or self.simulate_when_possible:
            try:
                json_response = self.faki.retrieve()
                simulated = "No data found" not in json_response
            except Exception as ee:
                error_service.record(ee, "Error retrieving Faki data")

        # Otherwise, get real Finti data
        # If not simulating, or if simulation attempt failed
        is_simulating = self.simulate or self.simulate_when_possible
        must_simulate = self.simulate and not self.simulate_when_possible
        if is_simulating and (simulated or must_simulate):
            if self.can_log():
                log.debug("Using simulated response")
        else:
            try:
                params = parameters if parameters else {}
                api_url = self.get_url(path)
                if self.max_logging():
                    log.info("Calling {0}".format(api_url))
                response = requests.get(
                    api_url,
                    params=params,
                    auth=self.auth,
                    verify=self.verify_certificate,
                    hooks={"response": self.handle_response},
                )
                json_response = response.text

                # If saving response data for later offline use
                if self.prepare_offline:
                    self.faki.save(json_response)
            except Exception as ee:
                error_service.record(ee, "Error retrieving Finti data")

        # Convert the JSON string into data
        response_data = json.loads(json_response) if json_response else None
        return self.finalize_response(response_data, include_metadata)

    def delete(self, path, parameters=None, include_metadata=False):
        """
        Make a DELETE call on Finti API
        :param path:             Finti path relative to root Finti URL
        :param parameters:       Object (map) of parameters to send to Finti
        :param include_metadata: Include status, version, result, jwt?              (default: False)

        Note: If using offline simulation, objects will not be removed, you'll just get a simulated successful response
        """
        params = {"path": path, "parameters": parameters}
        if self.can_log():
            log.trace(params)

        json_response = None

        # If simulating responses, or preparing to simulate them in the future, prepare a Faki instance
        if self.simulate or self.prepare_offline:
            self.faki = Faki(
                path, method="DELETE", parameters=parameters, payload=None, headers=None
            )

        # If getting offline data
        if self.simulate:
            try:
                json_response = self.faki.retrieve()
            except Exception as ee:
                error_service.record(ee, "Error retrieving Faki data")

        # Otherwise, get real Finti data
        else:
            try:
                params = parameters if parameters else {}
                api_url = self.get_url(path)
                if self.max_logging():
                    log.info("Calling {0}".format(api_url))

                response = requests.delete(
                    api_url,
                    params=params,
                    auth=self.auth,
                    verify=self.verify_certificate,
                    hooks={"response": self.handle_response},
                )
                json_response = response.text

                # If saving response data for later offline use
                if self.prepare_offline:
                    self.faki.save(json_response)

            except Exception as ee:
                error_service.record(ee, "Finti DELETE error")

        # Convert the JSON string into data
        response_data = json.loads(json_response) if json_response else None
        return self.finalize_response(response_data, include_metadata)

    def post(
        self,
        path,
        payload=None,
        headers=None,
        include_metadata=False,
        json_payload=None,
    ):

        if self.can_log():
            try:
                if payload and type(payload) is dict:
                    log_payload = dict(payload)

                    # Mask out anything that we would never want auto-logged
                    for kk in ["ssn"]:
                        if log_payload.get(kk):
                            log_payload[kk] = '*' * len(str(log_payload.get(kk)))
                else:
                    log_payload = payload
            except Exception as ee:
                error_service.record(ee, 'Logging Finti payload')
                log_payload = payload

            log_params = {"path": path, "payload": log_payload, "json_payload": json_payload}
            log.trace(log_params)

        # Special characters cannot be sent through Finti and result in unhandled exceptions
        # Remove any special characters that have not been encoded via Finti.encode_special_chars()
        if payload:
            try:
                for kk, vv in payload.items():
                    payload[kk], changed = validation_service.remove_special_characters(
                        vv
                    )
                    if changed:
                        log.warning(
                            f"Parameter {kk}'s special-characters have been altered."
                        )
            except Exception as ee:
                error_service.record(
                    ee, "Removing special characters from Finti parameters"
                )

        json_response = None

        # If simulating responses, or preparing to simulate them in the future, prepare a Faki instance
        if self.simulate or self.prepare_offline:
            self.faki = Faki(
                path,
                method="POST",
                parameters=json_payload,
                payload=payload,
                headers=headers,
            )

        # If getting offline data
        if self.simulate:
            try:
                json_response = self.faki.retrieve()
            except Exception as ee:
                error_service.record(ee, "Error retrieving Faki data")

        # Otherwise, get real Finti data
        else:
            try:
                api_url = self.get_url(path)
                headers = self.check_content_header(headers if headers else {})
                if self.max_logging():
                    log.info("Calling {0}".format(api_url))

                response = requests.post(
                    api_url,
                    data=payload if payload else {},
                    json=json_payload,
                    headers=headers,
                    auth=self.auth,
                    verify=self.verify_certificate,
                    hooks={"response": self.handle_response},
                )
                json_response = response.text

                # If saving response data for later offline use
                if self.prepare_offline:
                    self.faki.save(json_response)
            except Exception as ee:
                error_service.record(ee, "Finti POST error")

        # Convert the JSON string into data
        response_data = json.loads(json_response) if json_response else None
        return self.finalize_response(response_data, include_metadata)

    def put(
        self, path, payload=None, parameters=None, headers=None, include_metadata=False
    ):
        params = {"path": path, "parameters": parameters}
        if self.can_log():
            log.trace(params)

        json_response = None

        # If simulating responses, or preparing to simulate them in the future, prepare a Faki instance
        if self.simulate or self.prepare_offline:
            self.faki = Faki(
                path,
                method="PUT",
                parameters=parameters,
                payload=payload,
                headers=headers,
            )

        # If getting offline data
        if self.simulate:
            try:
                json_response = self.faki.retrieve()
            except Exception as ee:
                error_service.record(ee, "Error retrieving Faki data")

        # Otherwise, get real Finti data
        else:
            try:
                params = parameters if parameters else {}
                api_url = self.get_url(path)
                headers = self.check_content_header(headers if headers else {})
                if self.max_logging():
                    log.info("Calling {0}".format(api_url))

                response = requests.put(
                    api_url,
                    data=payload if payload else {},
                    headers=headers,
                    auth=self.auth,
                    verify=self.verify_certificate,
                    hooks={"response": self.handle_response},
                )
                json_response = response.text

                # If saving response data for later offline use, and a successful response was received
                if (
                    self.prepare_offline
                    and json_response
                    and "success" in json_response
                ):
                    self.faki.save(json_response)
            except Exception as ee:
                if self.can_log():
                    error_service.record(ee, "Finti PUT error")

        # Convert the JSON string into data
        response_data = json.loads(json_response) if json_response else None
        return self.finalize_response(response_data, include_metadata)

    def can_log(self):
        return not self.suppress_logging

    def max_logging(self):
        return not (self.suppress_logging or self.reduce_logging)

    def handle_response(self, response, *args, **kwargs):
        """No need to call this directly. This is called via the get method"""
        wdt_response = {
            "status": "",
            "result": "",
            "version": None,
            "jwt": None,
            "message": "",
        }
        try:
            wdt_response["status"] = response.status_code

            # Some responses have json-able content, some don't

            if response.status_code == requests.codes.OK:
                try:
                    response_data = response.json()
                    wdt_response["result"] = "success"

                    # Check if response structure is the same as wdt_response
                    if (
                        type(response_data) in [list, str]
                        or len(set(wdt_response.keys()).difference(set(response_data.keys()))) > 0
                    ):
                        wdt_response["message"] = response_data
                    else:
                        return response
                except Exception as ex:
                    response_data = response.text
                    wdt_response["result"] = "error"
                    wdt_response["message"] = response.text
                    if self.max_logging():
                        log.error("Non-JSON Response from Finti")

            elif response.status_code == requests.codes.NOT_FOUND:
                response_data = response.json()
                wdt_response["result"] = "not_found"

                # Check if response structure is the same as wdt_response
                if (
                    type(response_data) == str
                    or len(
                        set(wdt_response.keys()).difference(set(response_data.keys()))
                    )
                    > 0
                ):
                    wdt_response["message"] = response_data
                else:
                    return response

            else:
                if self.can_log():
                    log.error(f"API Unsuccessful:\n{response.text}", trace_error=False)
                else:
                    log.error("API Unsuccessful", trace_error=False)

                if response.status_code == requests.codes.FORBIDDEN:
                    wdt_response["result"] = "forbidden"
                else:
                    wdt_response["result"] = "error"
                message = ""
                try:
                    response_data = response.json()
                    if (
                        len(
                            set(wdt_response.keys()).difference(
                                set(response_data.keys())
                            )
                        )
                        > 0
                    ):
                        wdt_response["message"] = response_data
                    else:
                        return response
                    message = response_data["error"]
                except json.decoder.JSONDecodeError:
                    message = response.text
                    message_service.post_error(f"Non-JSON Response: {message}")
                except Exception as ee:
                    error_service.record(ee)
                    message = response.text
                wdt_response["message"] = message

        except Exception as ee:
            error_service.record(
                ee, response if self.can_log() else "Error handling Finti response"
            )

        # Overwrite content with wdt_response format
        response._content = json.dumps(wdt_response).encode("utf-8")
        return response

    def get_url(self, relative_path=""):
        """No need to call this directly. This is called via the get method"""
        return f"{self.finti_url}/{relative_path}".strip("/")

    def check_content_header(self, headers):
        if any(
            (True for ct in ["content-type", "Content-Type"] if ct in headers.keys())
        ):
            return headers
        return headers.update(self.content_type)

    def __init__(self, reduce_logging=False, suppress_logging=False):
        self.token = settings.FINTI_TOKEN
        self.finti_url = settings.FINTI_URL.strip("/")
        self.auth = (self.token, "")
        self.reduce_logging = reduce_logging
        self.suppress_logging = suppress_logging

        self.simulate = getattr(settings, "FINTI_SIMULATE_CALLS", False)
        self.simulate_when_possible = getattr(
            settings, "FINTI_SIMULATE_WHEN_POSSIBLE", False
        )
        self.prepare_offline = getattr(settings, "FINTI_SAVE_RESPONSES", False)

        # If simulating when possible, allow toggle on/off via UI
        # This is useful when cached data is outdated and needs to be refreshed
        if self.simulate_when_possible:
            if utility_service.get_session_var("finti_pause_simulation", False):
                self.simulate_when_possible = False

        # Verify certificate, except when running locally
        self.verify_certificate = True
        if utility_service.is_development():
            self.verify_certificate = self.finti_url.startswith("https://")

            # # Notify developer if using old Finti test URL
            # if 'ws-test' in self.finti_url and not utility_service.get_session_var('old_finti_notice'):
            #     message_service.post_warning(
            #         f"""
            #         You're using the old Finti test URL.<br>
            #         Please update to one of:
            #         <ul>
            #             <li>{self.finti_url.replace('ws-test', 'ws-dev')}</li>
            #             <li>{self.finti_url.replace('ws-test', 'ws-stage')}</li>
            #         </ul>
            #         """
            #     )
            #     utility_service.set_session_var('old_finti_notice', True)
