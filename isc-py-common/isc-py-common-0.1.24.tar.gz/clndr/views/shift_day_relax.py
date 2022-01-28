from clndr.models.shift_day_relax import Shift_day_relax, Shift_day_relaxManager
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Shift_day_relax_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Shift_day_relax.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Shift_day_relaxManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_relax_Add(request):
    return JsonResponse(DSResponseAdd(data=Shift_day_relax.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_relax_Update(request):
    return JsonResponse(DSResponseUpdate(data=Shift_day_relax.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_relax_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day_relax.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_relax_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day_relax.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_relax_Info(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day_relax.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_relax_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day_relax.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
