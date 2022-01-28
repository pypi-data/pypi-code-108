from django.urls import path

from isc_common.views import text_informations

urlpatterns = [

    path('Text_informations/Fetch/', text_informations.Text_informations_Fetch),
    path('Text_informations/Add', text_informations.Text_informations_Add),
    path('Text_informations/Update', text_informations.Text_informations_Update),
    path('Text_informations/Remove', text_informations.Text_informations_Remove),
    path('Text_informations/Lookup/', text_informations.Text_informations_Lookup),
    path('Text_informations/Info/', text_informations.Text_informations_Info),
    path('Text_informations/Copy', text_informations.Text_informations_Copy),

]
