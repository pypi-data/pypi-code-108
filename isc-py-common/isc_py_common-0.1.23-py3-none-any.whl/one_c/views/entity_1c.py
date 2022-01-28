from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from one_c.models.entity_1c import Entity_1c


@JsonResponseWithException()
def Entity_1c_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Entity_1c.objects.
                filter().
                get_range_rows1(
                request=request,
                # function=Entity_1cManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Entity_1c_Add(request):
    return JsonResponse(DSResponseAdd(data=Entity_1c.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Entity_1c_Update(request):
    return JsonResponse(DSResponseUpdate(data=Entity_1c.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Entity_1c_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Entity_1c.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Entity_1c_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Entity_1c.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Entity_1c_Info(request):
    return JsonResponse(DSResponse(request=request, data=Entity_1c.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
