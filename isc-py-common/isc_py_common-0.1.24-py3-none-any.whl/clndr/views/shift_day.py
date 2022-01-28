from clndr.models.shift_day import Shift_day, Shift_dayManager
from isc_common.common.functions import get_relation_field_name
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Shift_day_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Shift_day.objects.
                select_related(*get_relation_field_name( model=Shift_day )).
                get_range_rows1(
                request=request,
                function=Shift_dayManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_Add(request):
    return JsonResponse(DSResponseAdd(data=Shift_day.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_Update(request):
    return JsonResponse(DSResponseUpdate(data=Shift_day.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_Info(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Shift_day_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Shift_day.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
