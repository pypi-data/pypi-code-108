from django.urls import path

from isc_common.views import edited_by

urlpatterns = [

    path('Edited_by/Fetch/', edited_by.Edited_by_Fetch),
    path('Edited_by/Add', edited_by.Edited_by_Add),
    path('Edited_by/Update', edited_by.Edited_by_Update),
    path('Edited_by/Remove', edited_by.Edited_by_Remove),
    path('Edited_by/Lookup/', edited_by.Edited_by_Lookup),
    path('Edited_by/Info/', edited_by.Edited_by_Info),
    path('Edited_by/Copy', edited_by.Edited_by_Copy),

]
