"""
api blueprints group
"""


from sanic import Blueprint

from signal_cli_dbus_rest_api.api.about import about_v1
from signal_cli_dbus_rest_api.api.send import send_v1, send_v2
from signal_cli_dbus_rest_api.api.groups import groups_for_number, group_details
from signal_cli_dbus_rest_api.api.register_verify import register, verify
from signal_cli_dbus_rest_api.api.search import search_v1
from signal_cli_dbus_rest_api.api.reactions import reactions_v1


entrypoint = Blueprint.group(
    about_v1,
    send_v1,
    send_v2,
    groups_for_number,
    group_details,
    reactions_v1,
    register,
    search_v1,
    verify,
    url_prefix="/",
)
