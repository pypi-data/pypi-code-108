from typing import *

CSSColor = Text

WebSocketDataType = Union["message", "reload_browser", "refresh_chat_menu", "error", "refresh", "uploaded_file", "delivered", "readed"]


class ChatData:
    def __init__(self, kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

    channel: Text = None
    date: Text = None
    guid: Optional[Text] = None
    host: Text = None
    message: Optional[Text] = None
    message_state_delivered_id: int = None
    message_state_delivered_name: Text = None
    message_state_new_id: int = None
    message_state_new_name: Text = None
    message_state_not_readed_id: int = None
    message_state_not_readed_name: Text = None
    message_state_readed_id: int = None
    message_state_readed_name: Text = None
    not_: int = None
    path: Text = None
    port: int = None
    props: int = None
    theme_ids: List[int] = None
    type: WebSocketDataType = None
    user__color: Text = None
    user__full_name: Text = None
    user__short_name: Text = None
    user_id: int = None


class ChatResponseData(Dict):
    channel: Text
    date: Text
    guid: Text
    host: Text
    message: Text
    port: Text
    state__name: Optional[Text]
    to_whom_id: Optional[int]
    type: WebSocketDataType
    user__color: CSSColor
    user__short_name: Text
    user_id: int
