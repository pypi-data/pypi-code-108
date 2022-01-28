from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from one_c.models.param_type import Param_type


@JsonResponseWithException()
def Param_type_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Param_type.objects.
                filter().
                get_range_rows1(
                request=request,
                # function=Param_typeManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Param_type_Add(request):
    return JsonResponse(DSResponseAdd(data=Param_type.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Param_type_Update(request):
    return JsonResponse(DSResponseUpdate(data=Param_type.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Param_type_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Param_type.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Param_type_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Param_type.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Param_type_Info(request):
    return JsonResponse(DSResponse(request=request, data=Param_type.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
