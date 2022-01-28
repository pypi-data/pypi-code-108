from clndr.models.shifts import Shifts, ShiftsManager
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Shifts_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Shifts.objects.
                filter().
                get_range_rows1(
                request=request,
                function=ShiftsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shifts_Add(request):
    return JsonResponse(DSResponseAdd(data=Shifts.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shifts_Update(request):
    return JsonResponse(DSResponseUpdate(data=Shifts.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shifts_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Shifts.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shifts_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Shifts.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shifts_Info(request):
    return JsonResponse(DSResponse(request=request, data=Shifts.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shifts_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Shifts.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
