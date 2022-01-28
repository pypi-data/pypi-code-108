from clndr.models.calendar_shifts_days import Calendar_shifts_days, Calendar_shifts_daysManager
from isc_common.common.functions import get_relation_field_name
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Calendar_shifts_days_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Calendar_shifts_days.objects.
                select_related(*get_relation_field_name( model=Calendar_shifts_days )).
                get_range_rows1(
                request=request,
                function=Calendar_shifts_daysManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_shifts_days_Add(request):
    return JsonResponse(DSResponseAdd(data=Calendar_shifts_days.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_shifts_days_Update(request):
    return JsonResponse(DSResponseUpdate(data=Calendar_shifts_days.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_shifts_days_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Calendar_shifts_days.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_shifts_days_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Calendar_shifts_days.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_shifts_days_Info(request):
    return JsonResponse(DSResponse(request=request, data=Calendar_shifts_days.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendar_shifts_days_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Calendar_shifts_days.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
