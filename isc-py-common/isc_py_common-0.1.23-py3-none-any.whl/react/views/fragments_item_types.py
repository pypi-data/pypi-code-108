from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.fragments_item_types import Fragments_item_types, Fragments_item_typesManager


@JsonResponseWithException()
def Fragments_item_types_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fragments_item_types.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Fragments_item_typesManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_item_types_Add(request):
    return JsonResponse(DSResponseAdd(data=Fragments_item_types.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_item_types_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fragments_item_types.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_item_types_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_item_types.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_item_types_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_item_types.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_item_types_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_item_types.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_item_types_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_item_types.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
