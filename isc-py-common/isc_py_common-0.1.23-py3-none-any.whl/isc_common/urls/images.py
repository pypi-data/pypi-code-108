from django.urls import path

from isc_common.views import images
from isc_common.views.images import Images_Upload

urlpatterns = [

    path('Images/Fetch/', images.Images_Fetch),
    path('Images/Add', images.Images_Add),
    path('Images/Update', images.Images_Update),
    path('Images/Remove', images.Images_Remove),
    path('Images/Lookup/', images.Images_Lookup),
    path('Images/Info/', images.Images_Info),
    path('Images/Copy', images.Images_Copy),
    path('Images/Upload', Images_Upload),

]
