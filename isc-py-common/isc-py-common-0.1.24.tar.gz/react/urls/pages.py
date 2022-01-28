from django.urls import path

from react.views import pages

urlpatterns = [

    path('Pages/Fetch/', pages.Pages_Fetch),
    path('Pages/Add', pages.Pages_Add),
    path('Pages/Update', pages.Pages_Update),
    path('Pages/Remove', pages.Pages_Remove),
    path('Pages/Lookup/', pages.Pages_Lookup),
    path('Pages/Info/', pages.Pages_Info),
    path('Pages/Generate', pages.Pages_Generate),
    path('Pages/Copy', pages.Pages_Copy),

]
