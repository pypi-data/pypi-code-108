from django.urls import path

from react.views import page_fragments

urlpatterns = [

    path('Page_fragments/Fetch/', page_fragments.Page_fragments_Fetch),
    path('Page_fragments/Add', page_fragments.Page_fragments_Add),
    path('Page_fragments/Update', page_fragments.Page_fragments_Update),
    path('Page_fragments/Remove', page_fragments.Page_fragments_Remove),
    path('Page_fragments/Lookup/', page_fragments.Page_fragments_Lookup),
    path('Page_fragments/Info/', page_fragments.Page_fragments_Info),
    path('Page_fragments/Copy', page_fragments.Page_fragments_Copy),

]
