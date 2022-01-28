from django.urls import path

from refs.views import type_param

urlpatterns = [

    path('Type_param/Fetch/', type_param.Type_param_Fetch),
    path('Type_param/Add', type_param.Type_param_Add),
    path('Type_param/Update', type_param.Type_param_Update),
    path('Type_param/Remove', type_param.Type_param_Remove),
    path('Type_param/Lookup/', type_param.Type_param_Lookup),
    path('Type_param/Info/', type_param.Type_param_Info),
    path('Type_param/Copy', type_param.Type_param_Copy),

]
