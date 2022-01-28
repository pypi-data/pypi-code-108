from clndr.models.holidays import Holidays, HolidaysManager
from isc_common.common.functions import get_relation_field_name
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Holidays_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Holidays.objects.
                select_related(*get_relation_field_name( model=Holidays )).
                get_range_rows1(
                request=request,
                function=HolidaysManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Holidays_Add(request):
    return JsonResponse(DSResponseAdd(data=Holidays.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Holidays_Update(request):
    return JsonResponse(DSResponseUpdate(data=Holidays.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Holidays_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Holidays.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Holidays_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Holidays.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Holidays_Info(request):
    return JsonResponse(DSResponse(request=request, data=Holidays.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Holidays_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Holidays.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
