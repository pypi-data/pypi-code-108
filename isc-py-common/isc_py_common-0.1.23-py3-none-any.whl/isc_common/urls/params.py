from django.urls import path
from isc_common.views import params

urlpatterns = [

    path('Params/Fetch/', params.Params_Fetch),
    path('Params/Add', params.Params_Add),
    path('Params/Update', params.Params_Update),
    path('Params/Update1', params.Params_Update1),
    path('Params/Update2', params.Params_Update1),
    path('Params/Update3', params.Params_Update1),
    path('Params/Update4', params.Params_Update1),
    path('Params/Update5', params.Params_Update1),
    path('Params/Update6', params.Params_Update1),
    path('Params/Update7', params.Params_Update1),
    path('Params/Update8', params.Params_Update1),
    path('Params/Update9', params.Params_Update1),
    path('Params/Update10', params.Params_Update1),
    path('Params/Remove', params.Params_Remove),
    path('Params/Remove1', params.Params_Remove1),
    path('Params/Lookup', params.Params_Lookup),
    path('Params/Info/', params.Params_Info),
    path('Params/Get/', params.Params_Get),
    path('Params/GetKeyValue/', params.Params_GetKeyValue),

]
