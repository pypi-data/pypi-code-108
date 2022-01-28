from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages_whom import Messages_whom, Messages_whomManager


@JsonResponseWithException()
def Messages_whom_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages_whom.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Messages_whomManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_whom_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages_whom.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_whom_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages_whom.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_whom_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages_whom.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_whom_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages_whom.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_whom_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages_whom.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
