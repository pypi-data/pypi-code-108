"""
api blueprints group
"""


from sanic import Blueprint
from signal_cli_dbus_rest_api.api.about import about_v1
from signal_cli_dbus_rest_api.api.groups import (create_group_v1,
                                                 delete_group_v1,
                                                 group_details_v1,
                                                 groups_for_number_v1,
                                                 join_group_v1,
                                                 quit_group_v1,
                                                 update_group_v1)
from signal_cli_dbus_rest_api.api.reactions import reactions_v1
from signal_cli_dbus_rest_api.api.register_verify import register_v1, verify_v1
from signal_cli_dbus_rest_api.api.search import search_v1
from signal_cli_dbus_rest_api.api.send import send_v1, send_v2

entrypoint = Blueprint.group(
    about_v1,
    create_group_v1,
    delete_group_v1,
    groups_for_number_v1,
    group_details_v1,
    join_group_v1,
    quit_group_v1,
    reactions_v1,
    register_v1,
    search_v1,
    send_v1,
    send_v2,
    update_group_v1,
    verify_v1,
    url_prefix="/",
)
