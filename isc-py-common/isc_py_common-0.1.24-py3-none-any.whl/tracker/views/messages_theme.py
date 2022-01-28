from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages_theme import Messages_theme
from tracker.models.messages_theme_admin_view import Messages_theme_admin_view, Messages_theme_admin_view_Manager
from tracker.models.messages_theme_view import Messages_theme_view, Messages_theme_view_Manager


@JsonResponseWithException(printing=False, printing_res=False)
def Messages_theme_Fetch(request):
    _request = DSRequest(request)
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages_theme_view.objects.
                # filter().
                filter(users__overlap=[_request.user_id]).
                get_range_rows1(
                request=request,
                function=Messages_theme_view_Manager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException(printing=False, printing_res=False)
def Messages_theme_FetchAdmin(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Messages_theme_admin_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Messages_theme_admin_view_Manager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_theme_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages_theme.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_theme_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages_theme.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_theme_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages_theme.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_theme_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages_theme.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_theme_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages_theme_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
