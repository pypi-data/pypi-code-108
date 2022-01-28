from django.urls import path

from react.views import pages_view

urlpatterns = [

    path('Pages_view/Fetch/', pages_view.Pages_view_Fetch),
    path('Pages_view/Add', pages_view.Pages_view_Add),
    path('Pages_view/Update', pages_view.Pages_view_Update),
    path('Pages_view/Remove', pages_view.Pages_view_Remove),
    path('Pages_view/Lookup/', pages_view.Pages_view_Lookup),
    path('Pages_view/Info/', pages_view.Pages_view_Info),
    path('Pages_view/Copy', pages_view.Pages_view_Copy),

]
