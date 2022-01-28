from files_blk.models.files import Files
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Files_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Files.objects.
                select_related().
                get_range_rows1(
                request=request,
                # function=FilesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_Add(request):
    return JsonResponse(DSResponseAdd(data=Files.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_Update(request):
    return JsonResponse(DSResponseUpdate(data=Files.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Files.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Files.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_Info(request):
    return JsonResponse(DSResponse(request=request, data=Files.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Files.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
