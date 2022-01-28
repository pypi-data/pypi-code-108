from django.urls import path

from react.views import fragment_param_types

urlpatterns = [

    path('Fragment_param_types/Fetch/', fragment_param_types.Fragment_param_types_Fetch),
    path('Fragment_param_types/Add', fragment_param_types.Fragment_param_types_Add),
    path('Fragment_param_types/Update', fragment_param_types.Fragment_param_types_Update),
    path('Fragment_param_types/Remove', fragment_param_types.Fragment_param_types_Remove),
    path('Fragment_param_types/Lookup/', fragment_param_types.Fragment_param_types_Lookup),
    path('Fragment_param_types/Info/', fragment_param_types.Fragment_param_types_Info),
    path('Fragment_param_types/Copy', fragment_param_types.Fragment_param_types_Copy),

]
