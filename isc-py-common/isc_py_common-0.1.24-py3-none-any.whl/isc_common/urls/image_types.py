from django.urls import path

from isc_common.views import image_types

urlpatterns = [

    path('Image_types/Fetch/', image_types.Image_types_Fetch),
    path('Image_types/Add', image_types.Image_types_Add),
    path('Image_types/Update', image_types.Image_types_Update),
    path('Image_types/Remove', image_types.Image_types_Remove),
    path('Image_types/Lookup/', image_types.Image_types_Lookup),
    path('Image_types/Info/', image_types.Image_types_Info),
    path('Image_types/Copy', image_types.Image_types_Copy),

]
