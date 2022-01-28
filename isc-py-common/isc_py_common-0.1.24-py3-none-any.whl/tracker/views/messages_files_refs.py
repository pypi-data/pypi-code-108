from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages_files_refs import Messages_files_refs, Messages_files_refsManager


@JsonResponseWithException()
def Messages_files_refs_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages_files_refs.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Messages_files_refsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_refs_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages_files_refs.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_refs_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages_files_refs.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_refs_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files_refs.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_refs_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files_refs.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_refs_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files_refs.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_files_refs_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Messages_files_refs.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
