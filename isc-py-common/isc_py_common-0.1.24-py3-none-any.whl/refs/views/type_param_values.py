from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from refs.models.type_param_values import Type_param_values, Type_param_valuesManager


@JsonResponseWithException()
def Type_param_values_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Type_param_values.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Type_param_valuesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_values_Add(request):
    return JsonResponse(DSResponseAdd(data=Type_param_values.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_values_Update(request):
    return JsonResponse(DSResponseUpdate(data=Type_param_values.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_values_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Type_param_values.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_values_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Type_param_values.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_values_Info(request):
    return JsonResponse(DSResponse(request=request, data=Type_param_values.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Type_param_values_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Type_param_values.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
