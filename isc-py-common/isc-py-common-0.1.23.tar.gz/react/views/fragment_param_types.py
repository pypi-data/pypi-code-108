from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.fragment_param_types import Fragment_param_types, Fragment_param_typesManager


@JsonResponseWithException()
def Fragment_param_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fragment_param_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Fragment_param_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_param_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Fragment_param_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_param_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fragment_param_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_param_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_param_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_param_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_param_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_param_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_param_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_param_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_param_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
