from isc_common.http.DSResponse import DSResponseUpdate, DSResponseAdd, DSResponse, JsonResponseWithException
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.http.response import JsonResponse
from isc_common.models.text_informations import Text_informations, Text_informationsManager


@JsonResponseWithException()
def Text_informations_Fetch(request):
    return JsonResponse(
        DSResponse(
            request=request,
            data=Text_informations.objects.
                select_related().
                get_range_rows1(
                request=request,
                function=Text_informationsManager.getRecord
            ),
            status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Text_informations_Add(request):
    return JsonResponse(DSResponseAdd(data=Text_informations.objects.createFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Text_informations_Update(request):
    return JsonResponse(DSResponseUpdate(data=Text_informations.objects.updateFromRequest(request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Text_informations_Remove(request):
    return JsonResponse(DSResponse(request=request, data=Text_informations.objects.deleteFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Text_informations_Lookup(request):
    return JsonResponse(DSResponse(request=request, data=Text_informations.objects.lookupFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Text_informations_Info(request):
    return JsonResponse(DSResponse(request=request, data=Text_informations.objects.get_queryset().get_info(request=request), status=RPCResponseConstant.statusSuccess).response)


@JsonResponseWithException()
def Text_informations_Copy(request):
    return JsonResponse(DSResponse(request=request, data=Text_informations.objects.copyFromRequest(request=request), status=RPCResponseConstant.statusSuccess).response)
