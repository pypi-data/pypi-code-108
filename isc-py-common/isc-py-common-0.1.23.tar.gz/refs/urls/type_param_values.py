from django.urls import path

from refs.views import type_param_values

urlpatterns = [

    path('Type_param_values/Fetch/', type_param_values.Type_param_values_Fetch),
    path('Type_param_values/Add', type_param_values.Type_param_values_Add),
    path('Type_param_values/Update', type_param_values.Type_param_values_Update),
    path('Type_param_values/Remove', type_param_values.Type_param_values_Remove),
    path('Type_param_values/Lookup/', type_param_values.Type_param_values_Lookup),
    path('Type_param_values/Info/', type_param_values.Type_param_values_Info),
    path('Type_param_values/Copy', type_param_values.Type_param_values_Copy),

]
