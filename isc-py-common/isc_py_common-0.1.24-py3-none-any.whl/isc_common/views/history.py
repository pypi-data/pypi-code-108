from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.history import History


@JsonResponseWithException()
def History_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=History.objects.
                select_related().
                get_range_rows1(
                request=request,
                #function=XXX.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def History_Add(request):
    return JsonResponse(DSResponseAdd(data=History.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def History_Update(request):
    return JsonResponse(DSResponseUpdate(data=History.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def History_Remove(request):
    return JsonResponse(DSResponse(request=request, data=History.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def History_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=History.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def History_Info(request):
    return JsonResponse(DSResponse(request=request, data=History.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
