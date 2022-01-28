from events.models.event_type_users import Event_type_users, Event_type_usersManager
from isc_common.common.functions import get_relation_field_name
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Event_type_users_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Event_type_users.objects.
                select_related(*get_relation_field_name( model=Event_type_users )).
                get_range_rows1(
                request=request,
                function=Event_type_usersManager.getRecord,
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Event_type_users_Add(request):
    return JsonResponse(DSResponseAdd(data=Event_type_users.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Event_type_users_Update(request):
    return JsonResponse(DSResponseUpdate(data=Event_type_users.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Event_type_users_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Event_type_users.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Event_type_users_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Event_type_users.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Event_type_users_Info(request):
    return JsonResponse(DSResponse(request=request, data=Event_type_users.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Event_type_users_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Event_type_users.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
