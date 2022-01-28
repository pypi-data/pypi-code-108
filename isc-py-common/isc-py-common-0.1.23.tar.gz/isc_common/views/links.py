from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.links import Links, LinksManager


@JsonResponseWithException()
def Links_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Links.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=LinksManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Links_Add(request):
    return JsonResponse(DSResponseAdd(data=Links.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Links_Update(request):
    return JsonResponse(DSResponseUpdate(data=Links.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Links_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Links.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Links_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Links.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Links_Info(request):
    return JsonResponse(DSResponse(request=request, data=Links.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Links_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Links.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
