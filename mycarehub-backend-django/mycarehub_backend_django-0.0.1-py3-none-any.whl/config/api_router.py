from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from mycarehub.clients.views import (
    CaregiverViewSet,
    ClientFacilityViewSet,
    ClientViewSet,
    IdentifierViewSet,
    RelatedPersonViewSet,
    SecurityQuestionResponseViewSet,
    SecurityQuestionViewSet,
)
from mycarehub.common.views import FacilityViewSet, UserFacilityViewSet
from mycarehub.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("facilities", FacilityViewSet)
router.register("user_facilities", UserFacilityViewSet)
router.register("identifiers", IdentifierViewSet)
router.register("security_questions", SecurityQuestionViewSet)
router.register("security_question_responses", SecurityQuestionResponseViewSet)
router.register("related_persons", RelatedPersonViewSet)
router.register("clients", ClientViewSet)
router.register("client_facilities", ClientFacilityViewSet)
router.register("caregivers", CaregiverViewSet)

app_name = "api"
urlpatterns = router.urls
