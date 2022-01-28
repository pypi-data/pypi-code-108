import logging

from crypto.models.upload_file import DSResponse_UploadFile
from isc_common.datetime import DateToStr
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.ws.webSocket import WebSocket
from tracker.models.messages import Messages
from twits import ChatData, ChatResponseData

logger = logging.getLogger(__name__)


class DSResponse__Messages_Confirm_reading(DSResponse_UploadFile):

    def __init__(self, request):
        json_data = request.POST.dict()
        # logger.debug(f'json_data: {json_data}')

        chat_data = ChatData(json_data)

        try:
            for message in Messages.objects.filter(guid=chat_data.guid,
                                           to_whom_id=chat_data.user_id,
                                           state__in=[
                                               chat_data.message_state_not_readed_id,
                                           ]):
                message.state_id = chat_data.message_state_readed_id
                date = DateToStr(message.lastmodified, '%d.%m.%Y, %H:%M:%S')
                _message = ChatResponseData(
                    channel=chat_data.channel,
                    date=date,
                    guid=str(message.guid).upper(),
                    message=message.message,
                    state__name=message.state.name,
                    to_whom_id=message.to_whom.id,
                    type=chat_data.type,
                    user__color=message.user.color,
                    user__short_name=message.user.get_short_name,
                    user_id=message.user.id,
                )
                WebSocket.send_message(host=chat_data.host, port=chat_data.port, channel=chat_data.channel, message=_message, logger=logger)
                message.save()
                #TODO : НЕ идет отсюда сообщение, т.е. неизвестно куда приходит , посмотреть по channel consummers
        except Exception as ex:
            raise ex

        self.response = dict(status=RPCResponseConstant.statusSuccess)
