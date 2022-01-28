from files_blk.models.files_group import Files_group
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Files_group_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Files_group.objects.
                select_related().
                get_range_rows1(
                request=request,
                # function=Files_groupManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_group_Add(request):
    return JsonResponse(DSResponseAdd(data=Files_group.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_group_Update(request):
    return JsonResponse(DSResponseUpdate(data=Files_group.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_group_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Files_group.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_group_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Files_group.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_group_Info(request):
    return JsonResponse(DSResponse(request=request, data=Files_group.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Files_group_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Files_group.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
