from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from reports.models.jasper_reports import Jasper_reports, Jasper_reportsManager


@JsonResponseWithException()
def Jasper_reports_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Jasper_reports.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Jasper_reportsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_Add(request):
    return JsonResponse(DSResponseAdd(data=Jasper_reports.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_Update(request):
    return JsonResponse(DSResponseUpdate(data=Jasper_reports.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_Info(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Jasper_reports_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Jasper_reports.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
