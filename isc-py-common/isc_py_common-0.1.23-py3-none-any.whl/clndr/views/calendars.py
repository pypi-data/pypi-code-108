from clndr.models.calendars import Calendars, CalendarsManager
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Calendars_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Calendars.objects.
                filter().
                get_range_rows1(
                request=request,
                function=CalendarsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendars_Add(request):
    return JsonResponse(DSResponseAdd(data=Calendars.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendars_Update(request):
    return JsonResponse(DSResponseUpdate(data=Calendars.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendars_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Calendars.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendars_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Calendars.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendars_Info(request):
    return JsonResponse(DSResponse(request=request, data=Calendars.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Calendars_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Calendars.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
