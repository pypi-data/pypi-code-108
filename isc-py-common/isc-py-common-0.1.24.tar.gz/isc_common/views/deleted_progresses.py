from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.deleted_progresses import Deleted_progresses, Deleted_progressesManager


@JsonResponseWithException()
def Deleted_progresses_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Deleted_progresses.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Deleted_progressesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Deleted_progresses_Add(request):
    return JsonResponse(DSResponseAdd(data=Deleted_progresses.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Deleted_progresses_Update(request):
    return JsonResponse(DSResponseUpdate(data=Deleted_progresses.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Deleted_progresses_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Deleted_progresses.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Deleted_progresses_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Deleted_progresses.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Deleted_progresses_Info(request):
    return JsonResponse(DSResponse(request=request, data=Deleted_progresses.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Deleted_progresses_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Deleted_progresses.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
