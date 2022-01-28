from history.models.visitor import Visitor
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse


@JsonResponseWithException()
def Visitor_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Visitor.objects.
                filter().
                get_range_rows1(
                request=request,
                # function=VisitorManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Visitor_Add(request):
    return JsonResponse(DSResponseAdd(data=Visitor.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Visitor_Update(request):
    return JsonResponse(DSResponseUpdate(data=Visitor.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Visitor_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Visitor.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Visitor_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Visitor.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Visitor_Info(request):
    return JsonResponse(DSResponse(request=request, data=Visitor.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Visitor_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Visitor.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
