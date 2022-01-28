from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.debug import Debug


@JsonResponseWithException()
def Debug_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Debug.objects.
                select_related().
                get_range_rows1(
                request=request,
                # function=DebugManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Debug_Add(request):
    return JsonResponse(DSResponseAdd(data=Debug.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Debug_Update(request):
    return JsonResponse(DSResponseUpdate(data=Debug.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Debug_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Debug.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Debug_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Debug.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Debug_Info(request):
    return JsonResponse(DSResponse(request=request, data=Debug.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Debug_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Debug.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
