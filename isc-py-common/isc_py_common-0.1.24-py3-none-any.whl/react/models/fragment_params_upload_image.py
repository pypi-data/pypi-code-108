import logging

from django.db import transaction
from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.models.upload_image import Common_UploadImage

logger = logging.getLogger(__name__)


@JsonResponseWithException()
class DSResponse_Fragment_params_UploadImage(Common_UploadImage):
    def __init__(self, request):
        from react.models.fragment_params import Fragment_params

        with transaction.atomic():
            file = request.FILES.get('upload_attatch')

            if file is not None:
                image, image_type, fragment_id = self.upload_image(request=request)
                res = Fragment_params.objects.filter(id=fragment_id).update(image=image)
                logger.debug(f'Updated: {res}')


#http://192.168.0.61:8003/logic/Imgs/Download/2608758?code=fragment_params&path=fragment_params&main_model=fragment_params&main_model_id=12&ws_host=176.107.243.22&ws_port=8002&ws_channel=common
#http://192.168.0.61:8003/logic/Imgs/Download/2607889?code=fragment_params&path=fragment_params&main_model=fragment_params&main_model_id=3&ws_host=176.107.243.22&ws_port=8002&ws_channel=common
