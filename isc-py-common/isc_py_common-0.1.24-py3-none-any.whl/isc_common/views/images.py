from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.images import Images, ImagesManager
from isc_common.models.upload_image import DSResponse_UploadImage


@JsonResponseWithException()
def Images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=ImagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Images_Add(request):
    return JsonResponse(DSResponseAdd(data=Images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Images_Upload(request):
    return JsonResponse(DSResponse_UploadImage(request).response)
