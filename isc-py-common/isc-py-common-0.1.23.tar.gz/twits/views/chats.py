from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from twits.models.chats import Chats, ChatsManager


@JsonResponseWithException()
def Chats_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Chats.objects.
                filter().
                get_range_rows1(
                request=request,
                function=ChatsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chats_Add(request):
    return JsonResponse(DSResponseAdd(data=Chats.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chats_Update(request):
    return JsonResponse(DSResponseUpdate(data=Chats.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chats_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Chats.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chats_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Chats.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chats_Info(request):
    return JsonResponse(DSResponse(request=request, data=Chats.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Chats_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Chats.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
