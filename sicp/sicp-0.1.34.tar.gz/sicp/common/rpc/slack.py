from typing import Union

from common.rpc.utils import (
    create_service,
    requires_access_token,
    requires_master_secret,
)

service = create_service(__name__)


@requires_master_secret
@service.route("/api/list_channels")
def list_channels(*, course: str):
    ...


@requires_master_secret
@service.route("/api/post_message")
def post_message(*, course: str, message: Union[str, dict], channel: str):
    ...


@requires_access_token
@service.route("/api/list_conversations")
def list_conversations(*, course: str, include_dms: bool = False):
    ...


@requires_access_token
@service.route("/api/export_channel")
def export_channel(*, course: str, channel_id: str):
    ...


@requires_access_token
@service.route("/api/list_users")
def list_users(*, course: str):
    ...
