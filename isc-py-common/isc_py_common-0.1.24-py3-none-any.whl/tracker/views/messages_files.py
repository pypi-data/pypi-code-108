from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages_files import Messages_files, Messages_filesManager


@JsonResponseWithException()
def Messages_files_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages_files.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Messages_filesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages_files.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages_files.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


