from django.urls import path

from one_c.views import documents_param_1c

urlpatterns = [

    path('Documents_param_1c/Fetch/', documents_param_1c.Documents_param_1c_Fetch),
    path('Documents_param_1c/Add', documents_param_1c.Documents_param_1c_Add),
    path('Documents_param_1c/Update', documents_param_1c.Documents_param_1c_Update),
    path('Documents_param_1c/Remove', documents_param_1c.Documents_param_1c_Remove),
    path('Documents_param_1c/Lookup/', documents_param_1c.Documents_param_1c_Lookup),
    path('Documents_param_1c/Info/', documents_param_1c.Documents_param_1c_Info),

]
