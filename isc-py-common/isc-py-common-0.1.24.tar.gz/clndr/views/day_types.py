from clndr.models.day_types import Day_types, Day_typesManager
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Day_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Day_types.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Day_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Day_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Day_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Day_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Day_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Day_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Day_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Day_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
