from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.last_used_processes import Last_used_processes, Last_used_processesManager


@JsonResponseWithException()
def Last_used_processes_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Last_used_processes.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Last_used_processesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Last_used_processes_Add(request):
    return JsonResponse(DSResponseAdd(data=Last_used_processes.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Last_used_processes_Update(request):
    return JsonResponse(DSResponseUpdate(data=Last_used_processes.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Last_used_processes_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Last_used_processes.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Last_used_processes_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Last_used_processes.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Last_used_processes_Info(request):
    return JsonResponse(DSResponse(request=request, data=Last_used_processes.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Last_used_processes_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Last_used_processes.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
