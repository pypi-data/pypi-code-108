from django.urls import path

from react.views import page_level_types

urlpatterns = [

    path('Page_level_types/Fetch/', page_level_types.Page_level_types_Fetch),
    path('Page_level_types/Add', page_level_types.Page_level_types_Add),
    path('Page_level_types/Update', page_level_types.Page_level_types_Update),
    path('Page_level_types/Remove', page_level_types.Page_level_types_Remove),
    path('Page_level_types/Lookup/', page_level_types.Page_level_types_Lookup),
    path('Page_level_types/Info/', page_level_types.Page_level_types_Info),
    path('Page_level_types/Copy', page_level_types.Page_level_types_Copy),

]
