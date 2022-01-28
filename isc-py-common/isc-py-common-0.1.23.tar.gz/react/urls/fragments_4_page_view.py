from django.urls import path

from react.views import fragments_4_page_view

urlpatterns = [

    path('Fragments_4_page_view/Fetch/', fragments_4_page_view.Fragments_4_page_view_Fetch),
    path('Fragments_4_page_view/Add', fragments_4_page_view.Fragments_4_page_view_Add),
    path('Fragments_4_page_view/Update', fragments_4_page_view.Fragments_4_page_view_Update),
    path('Fragments_4_page_view/Remove', fragments_4_page_view.Fragments_4_page_view_Remove),
    path('Fragments_4_page_view/Lookup/', fragments_4_page_view.Fragments_4_page_view_Lookup),
    path('Fragments_4_page_view/Info/', fragments_4_page_view.Fragments_4_page_view_Info),
    path('Fragments_4_page_view/Copy', fragments_4_page_view.Fragments_4_page_view_Copy),

]
