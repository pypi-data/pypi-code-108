from django.urls import path

from one_c.views import entity_1c

urlpatterns = [

    path('Entity_1c/Fetch/', entity_1c.Entity_1c_Fetch),
    path('Entity_1c/Add', entity_1c.Entity_1c_Add),
    path('Entity_1c/Update', entity_1c.Entity_1c_Update),
    path('Entity_1c/Remove', entity_1c.Entity_1c_Remove),
    path('Entity_1c/Lookup/', entity_1c.Entity_1c_Lookup),
    path('Entity_1c/Info/', entity_1c.Entity_1c_Info),

]
