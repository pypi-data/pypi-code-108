import concurrent.futures
import json

from rest_framework import status

from common_structure_microservices.entity_url import EntityUrlMap
from common_structure_microservices.exception import GenericMicroserviceError
from common_structure_microservices.remote import RemoteModel


class SendNotification:

    def task_send_notification(self, request, notification_body):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.send_notification, request, notification_body)

    def send_notification(self, request, notification_body):
        remote_model = RemoteModel(request, url=EntityUrlMap.NOTIFICATION)
        send_notification = json.loads(remote_model.create(entity_data=notification_body).content)
        if not send_notification['status']:
            raise GenericMicroserviceError(detail=send_notification['errors'],
                                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
