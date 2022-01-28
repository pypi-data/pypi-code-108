from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.users_images import Users_images, Users_imagesManager


@JsonResponseWithException()
def Users_images_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Users_images.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Users_imagesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_images_Add(request):
    return JsonResponse(DSResponseAdd(data=Users_images.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_images_Update(request):
    return JsonResponse(DSResponseUpdate(data=Users_images.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_images_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Users_images.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_images_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Users_images.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_images_Info(request):
    return JsonResponse(DSResponse(request=request, data=Users_images.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Users_images_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Users_images.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
