from django.urls import path

from react.views import fragment_params

urlpatterns = [

    path('Fragment_params/Fetch/', fragment_params.Fragment_params_Fetch),
    path('Fragment_params/Add', fragment_params.Fragment_params_Add),
    path('Fragment_params/Update', fragment_params.Fragment_params_Update),
    path('Fragment_params/Remove', fragment_params.Fragment_params_Remove),
    path('Fragment_params/Lookup/', fragment_params.Fragment_params_Lookup),
    path('Fragment_params/Info/', fragment_params.Fragment_params_Info),
    path('Fragment_params/Copy', fragment_params.Fragment_params_Copy),
    path('Fragment_params/UploadImage', fragment_params.Fragment_params_ImagesUpload),

]
