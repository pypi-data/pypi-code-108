from ...models import PushNotification
from ..base import ApiBaseClass


class RootApi(ApiBaseClass):
    """ """

    def acknowledge_notification(
        self,
    ) -> PushNotification:
        """Acknowledge receiving of a notification



        Permissions:
            Must be logged in.
        Minimum Server Version:
            3.10
        """

        url = "/notifications/ack".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = PushNotification.parse_obj(response.json())

            return response_200
        return response
