import json
import datetime
from typing import Optional


class MessageFrame(object):
    """"
    Utility class to build messages frames, to send or received,
    defined in [foxbit web page](https://foxbit.com.br/api/#MessageFrame)"""

    PUBLIC_ENDPOINTS = (
        'LogOut',
        'GetInstrument',
        'GetInstruments',
        'GetProducts',
        'GetL2Snapshot',
        'GetTickerHistory',
        'SubscribeLevel1',
        'SubscribeLevel2',
        'SubscribeTicker',
        'SubscribeTrades',
        'UnsubscribeLevel1',
        'UnsubscribeLevel2',
        'UnsubscribeTicker',
        'UnsubscribeTrades'
    )

    PUBLIC_SUBSCRIBE_ENDPOINTS = (
        'TickerDataUpdateEvent',
        'Level1UpdateEvent',
        'Level2UpdateEvent',
        'TradeDataUpdateEvent'
    )

    PRIVATE_ENDPOINTS = (
        'GetUserConfig',
        'GetUserInfo',
        'GetUserPermissions',
        'SetUserConfig',
        'CancelAllOrders',
        'GetAccountInfo',
        'GetAccountPositions',
        'GetAccountTrades',
        'GetAccountTransactions',
        'GetInstrument',
        'GetInstruments',
        'GetOpenOrders',
        'SendOrder',
        'GetOrderFee',
        'GetOrderHistory',
        'GetDepositTickets',
        'GetWithdrawTickets'
    )

    def __init__(
        self,
        messageType: Optional[str] = 'request',
        sequenceNumber: Optional[int] = 0,
        endpoint: Optional[str] = 'LogOut',
        payload: Optional[dict] = {}
    ) -> None:
        """
        Build a message frame object,
        as defined in
        [foxbit web page](https://foxbit.com.br/api/#MessageFrame)

        Parameters
        ----------
        messageType: str
            default: 'request'
            Valid values are
                * 'request'
                * 'reply'
                * 'subscribe'
                * 'event'
                * 'unsubscribe'
                * 'error'

        sequenceNumber: int
            default: 0
            any integer

        endpoint: str
            default: 'LogOut'
            An foxbit [public](https://foxbit.com.br/api/#EndpointPublico)
            or [private](https://foxbit.com.br/api/#EndpointPrivado]
            endpoint

            See MessageFrame.PUBLIC_ENDPOINTS and
            MessageFrame.PRIVATE_ENDPOINTS and

        payload: dict
            The payload of message.
            Depends on `endpoint` argument.
            Check [documentation](https://foxbit.com.br/api/)
        """

        valid = not isinstance(messageType, str)
        valid = valid and not isinstance(messageType, str)
        if valid:
            msg = "messageType {} must be a str or int".format(messageType)
            raise TypeError(msg)
        if messageType == 'request':
            self.messageType = 0
        elif messageType == "reply":
            self.messageType = 1
        elif messageType == "subscribe":
            self.messageType = 2
        elif messageType == "event":
            self.messageType = 3
        elif messageType == "unsubscribe":
            self.messageType = 4
        elif messageType == "error":
            self.messageType = 5
        else:
            msg = "messageType {} not implemented".format(messageType)
            raise ValueError(msg)

        if not isinstance(sequenceNumber, int):
            raise TypeError("sequenceNumber must be an int")
        else:
            self.sequenceNumber = sequenceNumber

        if not isinstance(endpoint, str):
            raise TypeError("endpoint must be a str")

        # invalid value for endpoint
        inv = endpoint not in MessageFrame.PUBLIC_ENDPOINTS
        inv = inv and endpoint not in MessageFrame.PRIVATE_ENDPOINTS
        inv = inv and endpoint not in MessageFrame.PUBLIC_SUBSCRIBE_ENDPOINTS
        if inv:
            raise ValueError("endpoint {} not implemented".format(endpoint))
        else:
            self.endpoint = endpoint

        if isinstance(payload, dict) or isinstance(payload, list):
            self.payload = payload
        else:
            raise TypeError("payload must be a dict or a list")

    def __repr__(self):
        msg = "MessageFrame({'m': %i, 'i': %i, 'n': \'%s\', 'o': %s})"
        return msg % (
            self.messageType,
            self.sequenceNumber,
            self.endpoint,
            self.payload
        )

    def toJSON(self) -> str:
        """returns a JSON representation of instance"""
        return json.dumps({
            'm': self.messageType,
            'i': self.sequenceNumber,
            'n': self.endpoint,
            'o': json.dumps(self.payload)
        })

    @staticmethod
    def fromJSON(msg: Optional[str] = None):
        """returns a MessageFrame from a JSON representation"""
        res = json.loads(msg)

        if res['m'] == 0:
            m = 'request'
        elif res['m'] == 1:
            m = 'reply'
        elif res['m'] == 2:
            m = 'subscribe'
        elif res['m'] == 3:
            m = 'event'
        elif res['m'] == 4:
            m = 'unsubscribe'
        elif res['m'] == 5:
            m = 'error'
        else:
            msg = "messageType '{}' not implemented".format(res['m'])
            raise ValueError(msg)

        i = res['i']
        n = res['n']
        o = json.loads(res['o'])
        return MessageFrame(
            messageType=m,
            sequenceNumber=i,
            endpoint=n,
            payload=o
        )

    @staticmethod
    def buildValidPosixTimeString(
        dateAndtime: Optional[datetime.datetime] = None
    ) -> str:
        """"Get any date and convert to a valid Posix Time String,
        i.e. a time string in the format %Y-%m-%dT%H:%M:%S where
        %S will always be equal to zero (due to API responses)"""
        notvalid = dateAndtime is None
        notvalid = notvalid or not isinstance(dateAndtime, datetime.datetime)
        if notvalid:
            raise TypeError("date must be not None")
        convertedDate = datetime.datetime(
            dateAndtime.year,
            dateAndtime.month,
            dateAndtime.day,
            dateAndtime.hour,
            dateAndtime.minute,
            0
        )
        return convertedDate.strftime('%Y-%m-%dT%H:%M:%S')
