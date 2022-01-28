from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from one_c.models.document_1c import Document_1c


@JsonResponseWithException()
def Document_1c_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Document_1c.objects.
                filter().
                get_range_rows1(
                request=request,
                # function=Document_1cManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_1c_Add(request):
    return JsonResponse(DSResponseAdd(data=Document_1c.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_1c_Update(request):
    return JsonResponse(DSResponseUpdate(data=Document_1c.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_1c_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Document_1c.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_1c_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Document_1c.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Document_1c_Info(request):
    return JsonResponse(DSResponse(request=request, data=Document_1c.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
