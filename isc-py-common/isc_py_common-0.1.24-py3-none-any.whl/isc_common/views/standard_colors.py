from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.standard_colors import Standard_colors, Standard_colorsManager


@JsonResponseWithException()
def Standard_colors_Fetch(request):
    _request = DSRequest(request)
    return JsonResponse(
        DSResponse(
            request=request,
            data=Standard_colors.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Standard_colorsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Standard_colors_Add(request):
    return JsonResponse(DSResponseAdd(data=Standard_colors.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Standard_colors_Update(request):
    return JsonResponse(DSResponseUpdate(data=Standard_colors.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Standard_colors_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Standard_colors.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Standard_colors_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Standard_colors.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Standard_colors_Info(request):
    return JsonResponse(DSResponse(request=request, data=Standard_colors.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Standard_colors_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Standard_colors.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
