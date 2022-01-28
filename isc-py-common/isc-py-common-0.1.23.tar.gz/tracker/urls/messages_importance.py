from django.urls import path

from tracker.views import messages_importance

urlpatterns = [

    path('Messages_importance/Fetch/', messages_importance.Messages_importance_Fetch),
    path('Messages_importance/Add', messages_importance.Messages_importance_Add),
    path('Messages_importance/Update', messages_importance.Messages_importance_Update),
    path('Messages_importance/Remove', messages_importance.Messages_importance_Remove),
    path('Messages_importance/Lookup/', messages_importance.Messages_importance_Lookup),
    path('Messages_importance/Info/', messages_importance.Messages_importance_Info),
    path('Messages_importance/Copy', messages_importance.Messages_importance_Copy),

]
