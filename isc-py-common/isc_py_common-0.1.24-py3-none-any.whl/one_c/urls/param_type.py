from django.urls import path

from one_c.views import param_type

urlpatterns = [

    path('Param_type/Fetch/', param_type.Param_type_Fetch),
    path('Param_type/Add', param_type.Param_type_Add),
    path('Param_type/Update', param_type.Param_type_Update),
    path('Param_type/Remove', param_type.Param_type_Remove),
    path('Param_type/Lookup/', param_type.Param_type_Lookup),
    path('Param_type/Info/', param_type.Param_type_Info),

]
