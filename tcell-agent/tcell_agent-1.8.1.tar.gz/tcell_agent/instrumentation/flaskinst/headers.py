from tcell_agent.agent import TCellAgent
from tcell_agent.features.headers import add_headers
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.policies.policy_types import PolicyTypes


@catches_generic_exception(__name__, "Error inserting headers")
def flask_add_headers(request, response):
    if response.headers.get("Content-Type", None) and \
       response.headers["Content-Type"].startswith("text/html"):
        add_headers(response.headers, request._tcell_context)


@catches_generic_exception(__name__, "Error inserting headers to Werkzeug.exceptions.get_headers")
def werkzeug_additional_headers(request):
    headers = []

    headers_policy = TCellAgent.get_policy(PolicyTypes.HEADERS)
    tcell_headers = headers_policy.get_headers(request._tcell_context)

    for header_info in tcell_headers:
        header_name = header_info["name"]
        header_value = header_info["value"]
        headers.append((header_name, header_value))

    return headers
