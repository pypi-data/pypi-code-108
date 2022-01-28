from django.urls import path

from clndr.views import calendars

urlpatterns = [

    path('Calendars/Fetch/', calendars.Calendars_Fetch),
    path('Calendars/Add', calendars.Calendars_Add),
    path('Calendars/Update', calendars.Calendars_Update),
    path('Calendars/Remove', calendars.Calendars_Remove),
    path('Calendars/Lookup/', calendars.Calendars_Lookup),
    path('Calendars/Info/', calendars.Calendars_Info),
    path('Calendars/Copy', calendars.Calendars_Copy),

]
