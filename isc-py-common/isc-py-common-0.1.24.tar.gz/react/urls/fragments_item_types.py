from django.urls import path

from react.views import fragments_item_types

urlpatterns = [

    path('Fragments_item_types/Fetch/', fragments_item_types.Fragments_item_types_Fetch),
    path('Fragments_item_types/Add', fragments_item_types.Fragments_item_types_Add),
    path('Fragments_item_types/Update', fragments_item_types.Fragments_item_types_Update),
    path('Fragments_item_types/Remove', fragments_item_types.Fragments_item_types_Remove),
    path('Fragments_item_types/Lookup/', fragments_item_types.Fragments_item_types_Lookup),
    path('Fragments_item_types/Info/', fragments_item_types.Fragments_item_types_Info),
    path('Fragments_item_types/Copy', fragments_item_types.Fragments_item_types_Copy),

]
