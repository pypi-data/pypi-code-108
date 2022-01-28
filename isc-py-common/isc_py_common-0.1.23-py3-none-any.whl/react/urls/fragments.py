from django.urls import path

from react.views import fragments

urlpatterns = [

    path('Fragments/Fetch/', fragments.Fragments_Fetch),
    path('Fragments/Add', fragments.Fragments_Add),
    path('Fragments/Add_4_Page', fragments.Fragments_Add_4_Page),
    path('Fragments/Update', fragments.Fragments_Update),
    path('Fragments/Remove', fragments.Fragments_Remove),
    path('Fragments/Lookup/', fragments.Fragments_Lookup),
    path('Fragments/Info/', fragments.Fragments_Info),
    path('Fragments/Copy', fragments.Fragments_Copy),

]
