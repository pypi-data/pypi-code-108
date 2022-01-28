from isc_common.common.functions import get_relation_field_name
from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from tracker.models.messages import Messages
from tracker.models.messages_admin_view import Messages_admin_view, Messages_admin_viewManager
from tracker.models.messages_view import Messages_view, Messages_viewManager


@JsonResponseWithException()
def Messages_view_Fetch(request):
    response = DSResponse(
        request=request,
        data=Messages_view.objects.
            select_related(*get_relation_field_name( model=Messages_view )).
            # filter().
            filter().
            get_range_rows1(
            request=request,
            function=Messages_viewManager.getRecord
        ),
        status=RPCResponseConstant.statusSuccess).response
    return JsonResponse(response)


@JsonResponseWithException()
def Messages_view_FetchAdmin(request):
    _response = DSRequest(request)
    # print(_response.get_criteria())
    response = DSResponse(
        request=request,
        data=Messages_admin_view.objects.
            select_related(*get_relation_field_name( model=Messages_admin_view )).
            filter().
            get_range_rows1(
            request=request,
            function=Messages_admin_viewManager.getRecord
        ),
        status=RPCResponseConstant.statusSuccess).response
    return JsonResponse(response)


@JsonResponseWithException()
def Messages_view_Add(request):
    return JsonResponse(DSResponseAdd(data=Messages.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_view_Update(request):
    return JsonResponse(DSResponseUpdate(data=Messages.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_view_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Messages.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_view_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Messages.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Messages_view_Info(request):
    return JsonResponse(DSResponse(request=request, data=Messages.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)
