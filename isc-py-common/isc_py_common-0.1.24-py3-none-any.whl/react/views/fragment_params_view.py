from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.fragment_params_view import Fragment_params_view, Fragment_params_viewManager


@JsonResponseWithException()
def Fragment_params_view_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fragment_params_view.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Fragment_params_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Fragment_params_view.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fragment_params_view.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params_view.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params_view.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragment_params_view_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fragment_params_view.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
