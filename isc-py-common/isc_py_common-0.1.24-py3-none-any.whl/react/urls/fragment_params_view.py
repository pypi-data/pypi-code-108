from django.urls import path

from react.views import fragment_params_view

urlpatterns = [

    path('Fragment_params_view/Fetch/', fragment_params_view.Fragment_params_view_Fetch),
    path('Fragment_params_view/Add', fragment_params_view.Fragment_params_view_Add),
    path('Fragment_params_view/Update', fragment_params_view.Fragment_params_view_Update),
    path('Fragment_params_view/Remove', fragment_params_view.Fragment_params_view_Remove),
    path('Fragment_params_view/Lookup/', fragment_params_view.Fragment_params_view_Lookup),
    path('Fragment_params_view/Info/', fragment_params_view.Fragment_params_view_Info),
    path('Fragment_params_view/Copy', fragment_params_view.Fragment_params_view_Copy),

]
