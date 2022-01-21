from drf_braces.serializers.form_serializer import FormSerializer, make_form_serializer_field
from phonenumber_field.formfields import PhoneNumberField
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from mycarehub.clients.models import (
    Caregiver,
    Client,
    ClientFacility,
    HealthDiaryAttachment,
    Identifier,
    RelatedPerson,
    SecurityQuestion,
    SecurityQuestionResponse,
)

from .forms import ClientRegistrationForm


class IdentifierSerializer(ModelSerializer):
    class Meta:
        model = Identifier
        fields = "__all__"


class SecurityQuestionSerializer(ModelSerializer):
    class Meta:
        model = SecurityQuestion
        fields = "__all__"


class SecurityQuestionResponseSerializer(ModelSerializer):
    class Meta:
        model = SecurityQuestionResponse
        fields = "__all__"


class RelatedPersonSerializer(ModelSerializer):
    class Meta:
        model = RelatedPerson
        fields = "__all__"


class CaregiverSerializer(ModelSerializer):
    class Meta:
        model = Caregiver
        fields = "__all__"


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class ClientFacilitySerializer(ModelSerializer):
    class Meta:
        model = ClientFacility
        fields = "__all__"


class ClientRegistrationSerializer(FormSerializer):
    class Meta:
        form = ClientRegistrationForm
        fields = "__all__"
        field_mapping = {
            PhoneNumberField: make_form_serializer_field(CharField),
        }


class HealthDiaryAttachmentSerializer(ModelSerializer):
    class Meta:
        model = HealthDiaryAttachment
        fields = "__all__"
