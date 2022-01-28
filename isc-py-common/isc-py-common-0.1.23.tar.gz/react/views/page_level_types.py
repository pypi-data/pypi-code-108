from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.page_level_types import Page_level_types, Page_level_typesManager


@JsonResponseWithException()
def Page_level_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Page_level_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Page_level_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_level_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Page_level_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_level_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Page_level_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_level_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Page_level_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_level_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Page_level_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_level_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Page_level_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_level_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Page_level_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
