from django.urls import path

from one_c.views import document_1c

urlpatterns = [

    path('Document_1c/Fetch/', document_1c.Document_1c_Fetch),
    path('Document_1c/Add', document_1c.Document_1c_Add),
    path('Document_1c/Update', document_1c.Document_1c_Update),
    path('Document_1c/Remove', document_1c.Document_1c_Remove),
    path('Document_1c/Lookup/', document_1c.Document_1c_Lookup),
    path('Document_1c/Info/', document_1c.Document_1c_Info),

]
