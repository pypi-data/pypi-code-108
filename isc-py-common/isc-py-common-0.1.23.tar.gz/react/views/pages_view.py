from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.pages_view import Pages_view, Pages_viewManager


@JsonResponseWithException()
def Pages_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Pages_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Pages_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Pages_view.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Pages_view.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Pages_view.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Pages_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Pages_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Pages_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
