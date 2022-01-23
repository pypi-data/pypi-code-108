#!/usr/bin/python3
# Python REST CLI Tool, supporting classes
# Nicholas Schmidt
# 06 Mar 2021

# API Processing imports
import requests

# Command line validating imports
from django.core.validators import URLValidator

# JSON is how we import/export just about everything here...
import json

# Templates - use these to apply variables to URIs
from jinja2 import Environment, BaseLoader

# System calls for crashing
import sys


# Begin Supporting Classes
class Settings:
    # Initial Variable Settings
    #
    settings_file = {
        "settings": {
            "authentication": {
                "method": "basic",
                "certificate": "",
                "key": "",
            },
            "headers": {
                "content-type": "application/json",
                "X-Allow-Overwrite": "true",
            },
            "tls": {"validation": False},
            "verbosity": 1,
            "endpoint": "https://nsx.lab.engyak.net",
        },
        "plays": {},
        "errors": {
            "200": ["OK", "Request fulfilled, document follows"],
            "201": ["Created", "Document created, URL follows"],
            "202": ["Accepted", "Request accepted, processing continues off-line"],
            "203": ["Non-Authoritative Information", "Request fulfilled from cache"],
            "204": ["No Content", "Request fulfilled, nothing follows"],
            "205": ["Reset Content", "Clear input form for further input."],
            "206": ["Partial Content", "Partial content follows."],
            "300": ["Multiple Choices", "Object has several resources -- see URI list"],
            "301": ["Moved Permanently", "Object moved permanently -- see URI list"],
            "302": ["Found", "Object moved temporarily -- see URI list"],
            "303": ["See Other", "Object moved -- see Method and URL list"],
            "304": ["Not Modified", "Document has not changed since given time"],
            "305": [
                "Use Proxy",
                "You must use proxy specified in Location to access this resource.",
            ],
            "307": ["Temporary Redirect", "Object moved temporarily -- see URI list"],
            "400": ["Bad Request", "Bad request syntax or unsupported method"],
            "401": ["Unauthorized", "No permission -- see authorization schemes"],
            "402": ["Payment Required", "No payment -- see charging schemes"],
            "403": ["Forbidden", "Request forbidden -- authorization will not help"],
            "404": ["Not Found", "Nothing matches the given URI"],
            "405": [
                "Method Not Allowed",
                "Specified method is invalid for this server.",
            ],
            "406": ["Not Acceptable", "URI not available in preferred format."],
            "407": [
                "Proxy Authentication Required",
                "You must authenticate with this proxy before proceeding.",
            ],
            "408": ["Request Timeout", "Request timed out; try again later."],
            "409": ["Conflict", "Request conflict."],
            "410": ["Gone", "URI no longer exists and has been permanently removed."],
            "411": ["Length Required", "Client must specify Content-Length."],
            "412": ["Precondition Failed", "Precondition in headers is false."],
            "413": ["Request Entity Too Large", "Entity is too large."],
            "414": ["Request-URI Too Long", "URI is too long."],
            "415": ["Unsupported Media Type", "Entity body in unsupported format."],
            "416": ["Requested Range Not Satisfiable", "Cannot satisfy request range."],
            "417": ["Expectation Failed", "Expect condition could not be satisfied."],
            "500": ["Internal Server Error", "Server got itself in trouble"],
            "501": ["Not Implemented", "Server does not support this operation"],
            "502": ["Bad Gateway", "Invalid responses from another server/proxy."],
            "503": [
                "Service Unavailable",
                "The server cannot process the request due to a high load",
            ],
            "504": [
                "Gateway Timeout",
                "The gateway server did not receive a timely response",
            ],
            "505": ["HTTP Version Not Supported", "Cannot fulfill request."],
        },
    }

    # Return as JSON
    def get_settings_json(self):
        return json.dumps(self.settings_file, indent=4)


class Reliquary:

    # Initial Variable Settings
    #
    cogitation_verbosity = 0
    cogitation_certvalidation = True
    cogitation_username = ""
    cogitation_password = ""
    cogitation_authkey = ""
    cogitation_authcert = ""
    cogitation_headers = ""
    cogitation_endpoint = ""
    cogitation_bibliotheca = {}
    cogitation_errors = {}

    # We're pretty much picking up our configuration data
    def __init__(
        self, input_settings, input_user=None, input_pass=None, input_endpoint=None
    ):

        # Load Settings from JSON
        try:
            with open(input_settings, "r") as json_filehandle:
                json_settings = json.load(json_filehandle)
        except Exception as e:
            exit("E0000: Error Loading Settings File: " + str(e))

        try:
            # Let's start with basic global settings
            self.cogitation_verbosity = json_settings["settings"]["verbosity"]
            # Provide the option to specify the endpoint with the constructor, or pull it from the file
            if input_endpoint and input_endpoint is str:
                self.cogitation_endpoint = input_endpoint
            else:
                self.cogitation_endpoint = json_settings["settings"]["endpoint"]
            # TLS Tuning
            self.cogitation_certvalidation = json_settings["settings"]["tls"][
                "validation"
            ]
            # Authentication Settings
            self.cogitation_username = input_user
            self.cogitation_password = input_pass
            self.cogitation_authcert = json_settings["settings"]["authentication"][
                "certificate"
            ]
            self.cogitation_authkey = json_settings["settings"]["authentication"]["key"]
            # Load Known API Actions
            self.cogitation_headers = json_settings["settings"]["headers"]
            self.cogitation_bibliotheca = json_settings["plays"]
            # Load HTTP Errors
            self.cogitation_errors = json_settings["errors"]
        except Exception as e:
            print("E0002: Error Loading Settings! Settings Dictionary:")
            print(json.dumps(json_settings, indent=4))
            exit(str(e))

        self.validate_url(self.cogitation_endpoint)

    # Functions

    # Do API DELETE, using basic credentials
    def do_api_delete(self, do_api_uri, do_api_dryrun=False, do_api_json_pretty=False):
        # Perform API Processing - conditional basic authentication
        try:
            do_api_delete_url = self.cogitation_endpoint + do_api_uri
            self.validate_url(do_api_delete_url)
            if not do_api_dryrun:
                do_api_delete_r = requests.delete(
                    do_api_delete_url,
                    headers=self.cogitation_headers,
                    verify=self.cogitation_certvalidation,
                    auth=(self.cogitation_username, self.cogitation_password),
                )
                # We'll be discarding the actual `Response` object after this, but we do want to get HTTP status for erro handling
                response_code = do_api_delete_r.status_code
                print(response_code)
                do_api_delete_r.raise_for_status()  # trigger an exception before trying to convert or read data. This should allow us to get good error info
                if do_api_json_pretty:
                    return self.json_prettyprint(do_api_delete_r.text)
                else:
                    return do_api_delete_r.text  # if HTTP status is good, save response
            else:
                print(
                    json.dumps(
                        {
                            "do_api_get_headers": self.cogitation_headers,
                            "do_api_get_url": do_api_delete_url,
                        },
                        indent=4,
                    )
                )
        except requests.Timeout:
            print("E1000: API Connection timeout!")
        except requests.ConnectionError as connection_error:
            print(connection_error)
        except requests.HTTPError:
            if self.get_http_error_code(response_code):
                print(
                    "EA"
                    + str(response_code)
                    + ": HTTP Status Error "
                    + str(response_code)
                    + " "
                    + self.get_http_error_code(response_code)
                    + ": "
                    + do_api_delete_url
                )
                return do_api_delete_r.text
            else:
                print("EA999: Unhandled HTTP Error " + str(response_code) + "!")
        except requests.RequestException as requests_exception:
            print(requests_exception)
        except Exception as e:
            print(
                "E1002: Unhandled Requests exception! "
                + str(e)
                + " with endpoint "
                + do_api_delete_url
                + "and response "
                + do_api_delete_r.text
            )
            print(str(e))

    # Do API GET, using basic credentials
    def do_api_get(self, do_api_uri, do_api_dryrun=False, do_api_json_pretty=False):
        # Perform API Processing - conditional basic authentication
        try:
            do_api_get_url = self.cogitation_endpoint + do_api_uri
            self.validate_url(do_api_get_url)
            if not do_api_dryrun:
                do_api_get_r = requests.get(
                    do_api_get_url,
                    headers=self.cogitation_headers,
                    verify=self.cogitation_certvalidation,
                    auth=(self.cogitation_username, self.cogitation_password),
                )
                # We'll be discarding the actual `Response` object after this, but we do want to get HTTP status for erro handling
                response_code = do_api_get_r.status_code
                do_api_get_r.raise_for_status()  # trigger an exception before trying to convert or read data. This should allow us to get good error info
                if do_api_json_pretty:
                    return self.json_prettyprint(do_api_get_r.text)
                else:
                    return do_api_get_r.text  # if HTTP status is good, save response
            else:
                print(
                    json.dumps(
                        {
                            "do_api_get_headers": self.cogitation_headers,
                            "do_api_get_url": do_api_get_url,
                        },
                        indent=4,
                    )
                )
        except requests.Timeout:
            print("E1000: API Connection timeout!")
        except requests.ConnectionError as connection_error:
            print(connection_error)
        except requests.HTTPError:
            if self.get_http_error_code(response_code):
                print(
                    "EA"
                    + str(response_code)
                    + ": HTTP Status Error "
                    + str(response_code)
                    + " "
                    + self.get_http_error_code(response_code)
                    + ": "
                    + do_api_get_url
                )
                return do_api_get_r.text
            else:
                print("EA999: Unhandled HTTP Error " + str(response_code) + "!")
        except requests.RequestException as requests_exception:
            print(requests_exception)
        except Exception as e:
            print(
                "E1002: Unhandled Requests exception! "
                + str(e)
                + " with endpoint "
                + do_api_get_url
                + "and response "
                + do_api_get_r.text
            )
            print(str(e))

    # Do API POST, using basic credentials
    def do_api_pass(
        self,
        do_api_uri,
        do_api_verb="GET",
        do_api_payload=False,
        do_api_dryrun=False,
        do_api_json_pretty=False,
    ):
        # Perform API Processing - conditional basic authentication
        try:
            do_api_url = self.cogitation_endpoint + do_api_uri
            self.validate_url(do_api_url)
            if not do_api_dryrun and type(do_api_payload) is dict:
                do_api_r = requests.request(
                    do_api_verb,
                    url=do_api_url,
                    headers=self.cogitation_headers,
                    verify=self.cogitation_certvalidation,
                    auth=(self.cogitation_username, self.cogitation_password),
                    json=do_api_payload,
                )
                # We'll be discarding the actual `Response` object after this, but we do want to get HTTP status for erro handling
                response_code = do_api_r.status_code
                do_api_r.raise_for_status()  # trigger an exception before trying to convert or read data. This should allow us to get good error info
                if do_api_json_pretty:
                    return self.json_prettyprint(do_api_r.text)
                else:
                    return do_api_r.text  # if HTTP status is good, save response
            elif not do_api_dryrun and type(do_api_payload) is str:
                do_api_r = requests.request(
                    do_api_verb,
                    url=do_api_url,
                    headers=self.cogitation_headers,
                    verify=self.cogitation_certvalidation,
                    auth=(self.cogitation_username, self.cogitation_password),
                    data=do_api_payload,
                )
                # We'll be discarding the actual `Response` object after this, but we do want to get HTTP status for erro handling
                response_code = do_api_r.status_code
                do_api_r.raise_for_status()  # trigger an exception before trying to convert or read data. This should allow us to get good error info
                if do_api_json_pretty:
                    return self.json_prettyprint(do_api_r.text)
                else:
                    return do_api_r.text  # if HTTP status is good, save response
            else:
                do_api_dryrun_report = {
                    "do_api_get_headers": self.cogitation_headers,
                    "do_api_url": do_api_url,
                    "do_api_verb": do_api_verb,
                    "do_api_payload": json.loads(do_api_payload),
                }
                print(self.json_prettyprint(do_api_dryrun_report))
        except requests.Timeout:
            print("E1000: API Connection timeout!")
        except requests.ConnectionError as connection_error:
            print(connection_error)
        except requests.HTTPError:
            if self.get_http_error_code(response_code):
                print(
                    "EA"
                    + str(response_code)
                    + ": HTTP Status Error "
                    + str(response_code)
                    + " "
                    + self.get_http_error_code(response_code)
                    + ": "
                    + do_api_url
                )
                return do_api_r.text
            else:
                print("EA999: Unhandled HTTP Error " + str(response_code) + "!")
        except requests.RequestException as requests_exception:
            print(requests_exception)
        except Exception as e:
            print(
                "E1002: Unhandled Requests exception! "
                + str(e)
                + " with endpoint "
                + do_api_url
                + "and response "
                + do_api_r.text
            )
            print(str(e))

    # Executor of the API calls.
    # Takes optional arguments (variables, payload) depending on which method is used
    def namshub(
        self,
        namshub_string,
        namshub_variables=False,
        namshub_dryrun=False,
        namshub_payload=False,
        namshub_json_pretty=True,
    ):
        # Sanitize the verb used to uppercase, fewer changes for mixup
        namshub_verb = self.get_play_verb(namshub_string).lower().upper()
        # URI is in JSON file
        namshub_resource = self.get_play_uri(namshub_string)
        # Grab the namshub payload from the json file, if it exists
        # If it already exists, you don't need to load it
        if not namshub_payload:
            namshub_payload = self.get_play_payload(namshub_string)
        else:
            # This payload would normally be a file, but we can process input too
            # Let's fail-thru and try both methods
            namshub_payload = self.get_json_file_or_string(namshub_payload)
        # Test to see if either variables or payloads are required
        # If they're required and not present, don't proceed
        if self.get_play_requiresvariables(namshub_string) and not namshub_variables:
            sys.exit(
                "Error: Variables required by play, but not provided! Specify as a JSON dictionary with `--vars`"
            )
        if self.get_play_requiresbody(namshub_string) and not namshub_payload:
            sys.exit(
                "Error: Payload required by play, but not provided! Specify as a JSON dictionary with `-p`"
            )

        # Grab the variables, if it exists
        # From there, apply templates to whatever we can.
        if namshub_variables:
            namshub_variables = self.get_json_file_or_string(namshub_variables)
            namshub_resource = self.apply_template(namshub_resource, namshub_variables)
            # Check to see if the payload is a string before templating the payload
            if namshub_payload and namshub_payload is str:
                for i in namshub_variables:
                    if i in namshub_payload:
                        namshub_payload[i] = namshub_variables[i]

        # Make sure that the payload is a string before shippinng it to the API
        if namshub_payload and namshub_payload not in [str, dict]:
            try:
                namshub_payload = json.dumps(namshub_payload, indent=4)
            except Exception as e:
                sys.exit(
                    "Error processing API payload as "
                    + str(type(namshub_payload))
                    + " "
                    + str(e)
                )

        # Now that the transforms, testing, pre-processing are done, let's send to an API!
        if namshub_verb == "GET":
            return self.do_api_get(
                namshub_resource,
                do_api_dryrun=namshub_dryrun,
                do_api_json_pretty=namshub_json_pretty,
            )
        elif namshub_verb == "POST" or namshub_verb == "PATCH" or namshub_verb == "PUT":
            return self.do_api_pass(
                namshub_resource,
                do_api_payload=namshub_payload,
                do_api_verb=namshub_verb,
                do_api_dryrun=namshub_dryrun,
                do_api_json_pretty=namshub_json_pretty,
            )
        elif namshub_verb == "DELETE":
            return self.do_api_delete(
                namshub_resource,
                do_api_dryrun=namshub_dryrun,
                do_api_json_pretty=namshub_json_pretty,
            )
        else:
            sys.exit("Unsupported API verb " + namshub_verb + "!")

    # One-shot to apply templates to a given object string
    def apply_template(self, apply_template_template, apply_template_variables):
        try:
            j2template = Environment(loader=BaseLoader).from_string(
                apply_template_template
            )
            return j2template.render(apply_template_variables)
        except Exception as e:
            sys.exit(
                "Exception applying "
                + json.dumps(apply_template_variables)
                + " to "
                + apply_template_template
                + ". Error: "
                + str(e)
            )

    def validate_url(self, validate_url_url):
        # 99% solution here is to validate that a URL provided is valid. This doesn't test it or anything
        validate = URLValidator()
        try:
            validate(validate_url_url)
        except Exception as e:
            print(
                "E0001: Invalid URL Formatting. You provided: "
                + validate_url_url
                + 'Example: "https://www.abc.com/"'
            )
            exit(str(e))

    def json_prettyprint(self, json_prettyprint_input):
        # Print out in visually readable JSON
        if type(json_prettyprint_input) is dict:
            return json.dumps(json_prettyprint_input, indent=4)
        elif type(json_prettyprint_input) is str:
            try:
                return json.dumps(json.loads(json_prettyprint_input), indent=4)
            except Exception as e:
                sys.exit(
                    "Exception occurred while trying to pretty print the following:\r\n"
                    + e
                    + "\r\n"
                    + json_prettyprint_input
                )
        else:
            sys.exit(
                "Unknown Object Type: "
                + type(json_prettyprint_input)
                + "with a printed value of "
                + str(json_prettyprint_input)
            )

    def get_http_error_code(self, get_http_error_code_code):
        get_http_error_code_code = str(get_http_error_code_code)
        try:
            return json.dumps(
                self.cogitation_errors[get_http_error_code_code], indent=4
            )
        except KeyError:
            exit("Unknown HTTP Error Code: " + str(get_http_error_code_code) + " ")
        except Exception as e:
            exit("Exception fetching HTTP Error code" + str(e))

    # Fetch the URI for a given api call
    # Crash if it's not found
    def get_play_uri(self, get_play_name):
        try:
            return self.cogitation_bibliotheca[get_play_name]["uri"]
        except Exception as e:
            exit(
                "Exception fetching play URI: "
                + str(get_play_name)
                + ". Error: "
                + str(e)
            )

    # Return JSON string from `dict` payload for a given api call if successful
    # If not, return false and don't crash if a KeyError is returned
    # This object has no value as a `dict`, because its sent to a REST endpoint directly
    def get_play_payload(self, get_play_name):
        try:
            return self.cogitation_bibliotheca[get_play_name]["payload"]
        except KeyError:
            return False
        except Exception as e:
            exit("Exception fetching play requirement: " + str(get_play_name) + str(e))

    # Fetch what RESTful verb is to be used for a given api call
    # Crash if it's not found
    def get_play_verb(self, get_play_name):
        try:
            return self.cogitation_bibliotheca[get_play_name]["method"]
        except Exception as e:
            exit("Exception fetching play method: " + str(get_play_name) + str(e))

    # Fetch whether or not an api call requires a file payload
    def get_play_requiresbody(self, get_play_name):
        try:
            return self.cogitation_bibliotheca[get_play_name]["requiresbody"]
        except KeyError:
            return False
        except Exception as e:
            exit("Exception fetching play requirement: " + str(get_play_name) + str(e))

    # Fetch whether or not an api call requires variables
    def get_play_requiresvariables(self, get_play_name):
        try:
            return self.cogitation_bibliotheca[get_play_name]["requiresvariables"]
        except KeyError:
            return False
        except Exception as e:
            exit("Exception fetching play requirement: " + str(get_play_name) + str(e))

    def get_json_file(self, filename):
        # Load Settings from JSON
        try:
            with open(filename, "r") as json_filehandle:
                return json.load(json_filehandle)
        except Exception as e:
            exit("E0000: Error Loading Settings File " + filename + ": " + str(e))

    def get_json_file_or_string(self, input):
        # Recursive method to return a dictionary even if we're passed a dictionary
        if type(input) is dict:
            return input
        # Try to load as a string
        try:
            return json.loads(input)
        except Exception as e:
            if self.cogitation_verbosity:
                print(
                    "Tried to load as a string, and found the following error: "
                    + str(e)
                )
            try:
                # If it fails as a string, try to load as a file
                return self.get_json_file(input)
            except Exception as e:
                if self.cogitation_verbosity:
                    print(str(e))
                sys.exit(
                    "Error: " + input + " is neither a valid JSON string or filename!"
                )
