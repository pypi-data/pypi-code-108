from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

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
from mycarehub.clients.serializers import (
    CaregiverSerializer,
    ClientFacilitySerializer,
    ClientRegistrationSerializer,
    ClientSerializer,
    HealthDiaryAttachmentSerializer,
    IdentifierSerializer,
    RelatedPersonSerializer,
    SecurityQuestionResponseSerializer,
    SecurityQuestionSerializer,
)
from mycarehub.common.models.common_models import Contact, Facility
from mycarehub.users.models import User


class IdentifierViewSet(ModelViewSet):
    queryset = Identifier.objects.order_by("pk")
    serializer_class = IdentifierSerializer


class SecurityQuestionViewSet(ModelViewSet):
    queryset = SecurityQuestion.objects.order_by("pk")
    serializer_class = SecurityQuestionSerializer


class SecurityQuestionResponseViewSet(ModelViewSet):
    queryset = SecurityQuestionResponse.objects.order_by("pk")
    serializer_class = SecurityQuestionResponseSerializer


class RelatedPersonViewSet(ModelViewSet):
    queryset = RelatedPerson.objects.order_by("pk")
    serializer_class = RelatedPersonSerializer


class CaregiverViewSet(ModelViewSet):
    queryset = Caregiver.objects.order_by("pk")
    serializer_class = CaregiverSerializer


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.order_by("pk")
    serializer_class = ClientSerializer


class ClientFacilityViewSet(ModelViewSet):
    queryset = ClientFacility.objects.order_by("pk")
    serializer_class = ClientFacilitySerializer


class HealthDiaryAttachmentViewSet(ModelViewSet):
    queryset = HealthDiaryAttachment.objects.order_by("pk")
    serializer_class = HealthDiaryAttachmentSerializer


class ClientRegistrationView(APIView):
    queryset = Client.objects.all()  # to enable model permissions
    serializer_class = ClientRegistrationSerializer

    @transaction.atomic
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                request_user = request.user
                org = request_user.organisation
                flavour = "CONSUMER"

                new_user, _ = User.objects.get_or_create(
                    username=data["name"],
                    defaults={
                        "name": data["name"],
                        "gender": data["gender"],
                        "date_of_birth": data["date_of_birth"],
                        "user_type": "CLIENT",
                        "phone": data["phone_number"],
                        "flavour": flavour,
                        "organisation": org,
                    },
                )

                # create a contact, already opted in
                contact, _ = Contact.objects.get_or_create(
                    contact_value=data["phone_number"],
                    defaults={
                        "contact_type": "PHONE",
                        "contact_value": data["phone_number"],
                        "opted_in": True,
                        "flavour": flavour,
                        "user": new_user,
                        "organisation": org,
                        "created_by": request_user.pk,
                        "updated_by": request_user.pk,
                    },
                )

                # create an identifier (CCC)
                identifier, _ = Identifier.objects.get_or_create(
                    identifier_value=data["ccc_number"],
                    identifier_type="CCC",
                    defaults={
                        "identifier_use": "OFFICIAL",
                        "description": "CCC Number, Primary Identifier",
                        "is_primary_identifier": True,
                        "organisation": org,
                        "created_by": request_user.pk,
                        "updated_by": request_user.pk,
                    },
                )

                # retrieve the facility by the unique name
                facility_name = data["facility"]
                facility = Facility.objects.get(name=facility_name)

                # create a client
                client, _ = Client.objects.get_or_create(
                    user=new_user,
                    defaults={
                        "client_type": data["client_type"],
                        "user": new_user,
                        "enrollment_date": data["enrollment_date"],
                        "current_facility": facility,
                        "counselled": data["counselled"],
                        "organisation": org,
                        "created_by": request_user.pk,
                        "updated_by": request_user.pk,
                    },
                )

                # add the contact to the client
                client.contacts.add(contact)

                # add the identifier to the client
                client.identifiers.add(identifier)

                ClientFacility.objects.get_or_create(
                    client=client,
                    facility=facility,
                    defaults={
                        "organisation": org,
                        "created_by": request_user.pk,
                        "updated_by": request_user.pk,
                    },
                )

                # return the newly created client
                serialized_client = ClientSerializer(client)
                return Response(serialized_client.data, status=status.HTTP_201_CREATED)
            except Exception as e:  # noqa # pragma: nocover
                return Response(
                    {"exception": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )  # pragma: nocover
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
