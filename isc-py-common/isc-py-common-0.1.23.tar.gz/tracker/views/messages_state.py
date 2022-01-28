from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages_state import Messages_state, Messages_stateManager


@JsonResponseWithException()
def Messages_state_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages_state.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Messages_stateManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_state_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages_state.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_state_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages_state.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_state_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages_state.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)

@JsonResponseWithException()
def Messages_state_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages_state.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_state_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages_state.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
