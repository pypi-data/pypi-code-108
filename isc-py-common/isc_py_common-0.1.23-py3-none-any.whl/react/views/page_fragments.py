from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.page_fragments import Page_fragments, Page_fragmentsManager


@JsonResponseWithException()
def Page_fragments_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Page_fragments.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Page_fragmentsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_fragments_Add(request):
    return JsonResponse(DSResponseAdd(data=Page_fragments.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_fragments_Update(request):
    return JsonResponse(DSResponseUpdate(data=Page_fragments.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_fragments_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Page_fragments.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_fragments_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Page_fragments.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_fragments_Info(request):
    return JsonResponse(DSResponse(request=request, data=Page_fragments.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Page_fragments_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Page_fragments.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
