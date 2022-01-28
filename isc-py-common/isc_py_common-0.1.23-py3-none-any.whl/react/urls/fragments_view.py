from django.urls import path

from react.views import fragments_view

urlpatterns = [

    path('Fragments_view/Fetch/', fragments_view.Fragments_view_Fetch),
    path('Fragments_view/Add', fragments_view.Fragments_view_Add),
    path('Fragments_view/Update', fragments_view.Fragments_view_Update),
    path('Fragments_view/Remove', fragments_view.Fragments_view_Remove),
    path('Fragments_view/Lookup/', fragments_view.Fragments_view_Lookup),
    path('Fragments_view/Info/', fragments_view.Fragments_view_Info),
    path('Fragments_view/Copy', fragments_view.Fragments_view_Copy),

]
