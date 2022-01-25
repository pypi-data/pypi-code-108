import sys
import json

CLI_DOCS_URL = 'https://docs.cloud.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/'
NON_SERVICE_COMMANDS = ['setup', 'raw-request', 'session']
DOCS_EXAMPLE_DIR = 'docs/doc-gen/examples/'
GENERATE_ALL = False if len(sys.argv) == 2 else True
SERVICE_DIRECTORY = sys.argv[1] if len(sys.argv) == 2 else 'None'
COMMAND_NAMES_TO_SPEC_NAMES = {}
LINK_REPLACEMENTS = {}


def find_id_in_response(response):
    """Finds the ID of the response data. Response must be JSON."""
    try:
        return json.loads(response)['data']['id']
    except Exception:
        raise RuntimeError("Could not parse id from json response: " + response)


def get_required_and_optional_params(params):
    req_params = [param for param in
                  filter(lambda param: param.help.endswith(' [required]'), params)]
    opt_params = [param for param in filter(lambda param: param not in req_params, params)]
    req_params.sort(key=lambda param: param.name)
    opt_params.sort(key=lambda param: param.name)

    return req_params, opt_params
