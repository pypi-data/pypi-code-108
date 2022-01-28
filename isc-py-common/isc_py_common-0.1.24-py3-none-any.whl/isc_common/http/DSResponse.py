import json
import logging
import math
import pprint
import sys
import traceback

from django.conf import settings
from django.db.models import QuerySet, Model
from django.forms import model_to_dict
from websocket import create_connection

from isc_common import setAttr, Wrapper, user_name_anonim
from isc_common.common.functions import Common
from isc_common.http.DSRequest import RequestData, DSRequest
from isc_common.http.RPCResponse import RPCResponse, RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.json import BytesToJson

logger = logging.getLogger(__name__)


class Exception_WS_Enabled(Exception):
    pass


class BodyWrapper(Wrapper):
    data = None
    login = None
    json = None
    httpHeaders = None
    transaction = None


class Body:
    session = None

    def __init__(self, body, session):
        self.session = session
        if isinstance(body, dict):
            self.body = body
        else:
            body = BytesToJson(body)
        self.body = BodyWrapper(**body)
        if self.body.transaction is not None:
            operations = self.body.transaction.get('operations')
            if isinstance(operations, list):
                for operation in operations:
                    data = operation.get('data')
                    httpHeaders = data.get('httpHeaders')
                    if isinstance(httpHeaders, dict):
                        self.body.httpHeaders = httpHeaders
                        break

        if self.body.httpHeaders is not None:
            self.body.httpHeaders = Wrapper(**self.body.httpHeaders)
        elif self.body.data is not None and self.body.data.get('httpHeaders') is not None:
            self.body.httpHeaders = Wrapper(**self.body.data.get('httpHeaders'))

    @property
    def login(self):
        from isc_common.auth.models.user import User
        if self.body.login is not None:
            return self.body.login
        elif self.body.httpHeaders is not None and self.body.httpHeaders.USER_ID:
            return User.objects.get(id=self.body.httpHeaders.USER_ID).username
        else:
            if self.session is not None and hasattr(self.session, '_session_cache') and self.session._session is not None:
                ws_channel = self.session._session.get('ws_channel')
                if ws_channel is not None:
                    return ws_channel.split('_')[1]
                else:
                    return user_name_anonim
            elif self.session is None:
                return user_name_anonim
            elif hasattr(self.session, '_session_cache') is False or self.session._session is None:
                return user_name_anonim

    @property
    def user(self):
        from isc_common.auth.models.user import User
        if self.body.login is not None:
            try:
                return User.objects.get(username=self.body.login)
            except User.DoesNotExist:
                raise Exception('user not enable type')
        elif self.body.httpHeaders is not None and self.body.httpHeaders.USER_ID:
            return User.objects.get(id=self.body.httpHeaders.USER_ID)
        else:
            if self.session is not None and self.session._session is not None:
                try:
                    ws_channel = self.session._session.get('ws_channel')
                    if ws_channel is not None:
                        return User.objects.get(username=ws_channel.split('_')[1])
                    else:
                        return User.objects.get(username=user_name_anonim)
                except User.DoesNotExist:
                    raise Exception('user not enable type')
            else:
                raise Exception('user not enable type')


def JsonWSResponseWithException(printing=False, printing_res=False):
    def JsonWSResponseWithExceptionInner(func):
        def print_in(o, str=None):
            pp = pprint.PrettyPrinter(indent=4)

            if str:
                print(f"=========== Begin {str} ========================")
            else:
                print(f"=========== Begin {o.__class__.__name__} ========================")
            if isinstance(o, dict):
                pp.pprint(RequestData(o).getDataWithOutField(['pp', '_state']).dict())
            elif isinstance(o, object):
                pp.pprint(RequestData(o.__dict__).getDataWithOutField(['pp', '_state']).dict())

            if str:
                print(f"=========== End   {str} ========================")
            else:
                print(f"=========== End   {o.__class__.__name__} ========================")
            print("\n")

        def wrapper(*args, **kwargs):
            from isc_common.json import BytesToJson
            request = args[0]

            port = request.GET.get('ws_port')
            if port is None:
                port = request.GET.get('port')
                if port is None:
                    port = settings.WS_PORT
                    if port is None:
                        raise Exception_WS_Enabled(Common.arraund_error('Do not have ws_port'))

            host = request.GET.get('ws_host')
            if host is None:
                host = request.GET.get('host')
                if host is None:
                    host = settings.WS_HOST
                    if host is None:
                        raise Exception_WS_Enabled(Common.arraund_error('Do not have ws_host'))

            channel = request.GET.get('ws_channel')
            if channel is None:
                body = BytesToJson(request.body)
                body = Body(body, request.session)
                if settings.WS_CHANNEL is not None:
                    channel = f'''{settings.WS_CHANNEL}_{body.login}'''

            try:
                if printing:
                    _request = DSRequest(request)
                    print_in(_request)
                    print_in(request.COOKIES, 'request.COOKIES')
                    print_in(request.GET, 'request.GET')
                    print_in(request.POST, 'request.POST')
                    print_in(request.META, 'request.META')

                res = func(*args, **kwargs)
                if printing_res:
                    print_in(res)

                return res
            except Exception as ex:
                exc_info = sys.exc_info()
                stackTrace = traceback.format_exception(*exc_info)
                message = str(ex)

                try:
                    ws = create_connection(f"ws://{host}:{port}/ws/{channel}/")
                    ws.send(json.dumps(dict(message=message, stackTrace=stackTrace, type="error")))
                    ws.close()
                except Exception as ex:

                    exc_info = sys.exc_info()
                    message = str(ex)
                    stackTrace = traceback.format_exception(*exc_info)

                    logging.error(message)

                    for x in stackTrace:
                        logger.error(x)

                    del exc_info

                for x in stackTrace:
                    logger.error(x)

                return JsonResponse(DSResponseOk().response)

        return wrapper

    return JsonWSResponseWithExceptionInner


def JsonResponseWithException(printing=False, printing_res=False):
    return JsonWSResponseWithException(printing=printing, printing_res=printing_res)


def JsonResponseWithExceptionOld(printing=False, printing_res=False):
    return JsonWSResponseWithException(printing=printing, printing_res=printing_res)


def JsonWSPostResponseWithException(printing=False, printing_res=False):
    return JsonWSResponseWithException(printing=printing, printing_res=printing_res)


class DSResponse(RPCResponse):

    def normal_round(self, n):
        if n - math.floor(n) < 0.5:
            return math.floor(n)
        return math.ceil(n)

    def __init__(self,
                 request,
                 clientContext=None,
                 data=None,
                 message=None,
                 stackTrace=None,
                 httpHeaders=None,
                 httpResponseCode=None,
                 httpResponseText=None,
                 status=RPCResponseConstant.statusSuccess,
                 transactionNum=None,
                 dataSource=None,
                 errors=None,
                 invalidateCache=None,
                 operationId=None,
                 operationType=None,
                 queueStatus=None,
                 totalRows=None
                 ):
        RPCResponse.__init__(self,
                             clientContext=clientContext,
                             data=data,
                             httpHeaders=httpHeaders,
                             httpResponseCode=httpResponseCode,
                             httpResponseText=httpResponseText,
                             status=status,
                             transactionNum=transactionNum)

        request = DSRequest(request=request) if request else None
        self.dataSource = dataSource
        self.endRow = request.endRow if request else None
        self.startRow = request.startRow if request else None
        self.drawAheadRatio = request.drawAheadRatio if request else 1.2
        self.errors = errors
        self.invalidateCache = invalidateCache
        self.operationId = operationId
        self.operationType = operationType
        self.queueStatus = queueStatus

        self.message = message
        self.stackTrace = stackTrace
        self.status = status

        if isinstance(data, QuerySet):
            data = list(data)

        if isinstance(data, list):

            if self.startRow is not None and self.endRow is not None:
                qty = self.endRow - self.startRow
                len_data = len(self.data)

                if len_data == 0:
                    self.totalRows = 0
                else:
                    if len_data == qty:
                        self.totalRows = self.startRow + self.normal_round(qty * self.drawAheadRatio)
                    else:
                        self.totalRows = self.startRow + len_data

                # logger.debug(f'startRow: {self.startRow}, endRow: {self.endRow}, qty: {qty}, len_data: {len_data}, totalRows: {self.totalRows}')
            else:
                self.totalRows = totalRows
        else:
            self.totalRows = totalRows

    @property
    def response(self):
        setAttr(self.dict, 'startRow', self.startRow)
        setAttr(self.dict, 'endRow', self.endRow)
        setAttr(self.dict, 'totalRows', self.totalRows)
        # logger.debug(f'self.dict: {self.dict}')
        return dict(response=self.dict)


class DSResponseAdd(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )


class DSResponseCopy(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )


class DSResponseUpdate(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

        @property
        def response(self):
            return dict(response=dict(status=self.status, data=self.data))


class DSResponseLookup(DSResponse):
    def __init__(self, data, status):
        if isinstance(data, Model):
            data = [model_to_dict(data)]

        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=data,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=status,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

        @property
        def response(self):
            return dict(response=dict(status=self.status, data=self.data))


class DSResponseOk(DSResponse):
    def __init__(self):
        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            data=[],
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=RPCResponseConstant.statusSuccess,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

    @property
    def response(self):
        return dict(response=dict(status=self.status))


class DSResponseFailure(DSResponse):
    def __init__(self,
                 message=None,
                 stackTrace=None
                 ):
        DSResponse.__init__(self,
                            request=None,
                            clientContext=None,
                            message=message,
                            stackTrace=stackTrace,
                            httpHeaders=None,
                            httpResponseCode=None,
                            httpResponseText=None,
                            status=RPCResponseConstant.statusFailure,
                            transactionNum=None,
                            dataSource=None,
                            errors=None,
                            invalidateCache=None,
                            operationId=None,
                            operationType=None,
                            queueStatus=None,
                            totalRows=None,
                            )

    @property
    def response(self):
        return dict(response=dict(
            status=-1,
            data=dict(
                error=dict(
                    message=self.message,
                    stackTrace=self.stackTrace
                )
            )
        ))
