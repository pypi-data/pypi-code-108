from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.image_types import Image_types, Image_typesManager


@JsonResponseWithException()
def Image_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Image_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Image_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Image_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Image_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Image_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Image_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Image_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Image_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Image_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Image_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Image_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Image_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Image_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Image_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
