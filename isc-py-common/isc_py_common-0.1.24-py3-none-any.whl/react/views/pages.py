from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.pages import Pages
from react.models.pages_view import Pages_view, Pages_viewManager


@JsonResponseWithException()
def Pages_Fetch(request):
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
def Pages_Add(request):
    return JsonResponse(DSResponseAdd(data=Pages.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_Update(request):
    return JsonResponse(DSResponseUpdate(data=Pages.objects.updateFromRequest(request, propsArr=['application']), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Pages.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Pages.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_Info(request):
    return JsonResponse(DSResponse(request=request, data=Pages_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_Generate(request):
    return JsonResponse(DSResponse(request=request, data=Pages.objects.generateFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Pages_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Pages.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
