from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from reports.models.jasper_reports_users import Jasper_reports_users, Jasper_reports_usersManager


@JsonResponseWithException()
def Jasper_reports_users_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Jasper_reports_users.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Jasper_reports_usersManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_users_Add(request):
    return JsonResponse(DSResponseAdd(data=Jasper_reports_users.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_users_Update(request):
    return JsonResponse(DSResponseUpdate(data=Jasper_reports_users.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_users_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports_users.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_users_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports_users.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_users_Info(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports_users.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_users_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports_users.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
