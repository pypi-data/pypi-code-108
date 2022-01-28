from isc_common.http.DSRequest import DSRequest
from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from react.models.fragments import Fragments
from react.models.fragments_view import Fragments_view, Fragments_viewManager


@JsonResponseWithException()
def Fragments_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Fragments_view.objects.
                filter().
                get_range_rows1(
                request=request,
                function=Fragments_viewManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)

@JsonResponseWithException()
def Fragments_Add(request):
    return JsonResponse(DSResponseAdd(data=Fragments.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)

@JsonResponseWithException()
def Fragments_Add_4_Page(request):
    return JsonResponse(DSResponseAdd(data=Fragments.objects.create4PageFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_Update(request):
    return JsonResponse(DSResponseUpdate(data=Fragments.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Fragments.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)

@JsonResponseWithException()
def Fragments_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Fragments.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_Info(request):
    return JsonResponse(DSResponse(request=request, data=Fragments_view.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Fragments_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Fragments.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
