import concurrent.futures
import json

from rest_framework import status

from common_structure_microservices.entity_url import EntityUrlMap
from common_structure_microservices.exception import GenericMicroserviceError
from common_structure_microservices.remote import RemoteModel


class DeleteNotification:

    def task_delete_notification(self, request, notification_body):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.do_delete_notification, request, notification_body)

    def do_delete_notification(self, request, entity_data):
        remote_model = RemoteModel(request, url=EntityUrlMap.NOTIFICATION)
        delete_notification = json.loads(remote_model.create(entity_data=entity_data,
                                                             url_path='delete_invitation_community/').content)
        if not delete_notification['status']:
            raise GenericMicroserviceError(detail=delete_notification['errors'],
                                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
