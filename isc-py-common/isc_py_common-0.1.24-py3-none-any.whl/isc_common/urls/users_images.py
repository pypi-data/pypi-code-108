from django.urls import path

from isc_common.views import users_images

urlpatterns = [

    path('Users_images/Fetch/', users_images.Users_images_Fetch),
    path('Users_images/Add', users_images.Users_images_Add),
    path('Users_images/Update', users_images.Users_images_Update),
    path('Users_images/Remove', users_images.Users_images_Remove),
    path('Users_images/Lookup/', users_images.Users_images_Lookup),
    path('Users_images/Info/', users_images.Users_images_Info),
    path('Users_images/Copy', users_images.Users_images_Copy),

]
