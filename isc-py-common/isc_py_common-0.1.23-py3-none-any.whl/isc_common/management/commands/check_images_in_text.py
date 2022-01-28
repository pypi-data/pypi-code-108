import logging
import os
import re

from django.conf import settings
from django.core.management import BaseCommand
from isc_common.fields.files import make_REPLACE_IMAGE_PATH
from isc_common.models.text_informations import Text_informations
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        query = Text_informations.objects.filter().order_by('id')
        pbar = tqdm(total=query.count())
        o_ssh_client = settings.SSH_CLIENTS.client(settings.OLD_FILES)

        exp = r'(?i)(src|width|height|alt)=\"(.*?)\"'

        for item in query:
            for name, value in re.findall(exp, item.text):
                if name == 'src' and value.find('http:') == -1:
                    full_name_image_replaced = make_REPLACE_IMAGE_PATH(value)
                    if full_name_image_replaced == value:
                        full_name_image_replaced = f"{settings.PATH_IMAGES_REPLACE.get('new_path')}{value.replace('..', f'{os.sep}lflru')}"

                    if o_ssh_client.exists(full_name_image_replaced):
                        logger.debug(f'\nid: {item.id} {value}')
                    else:
                        logger.debug(f'\n{full_name_image_replaced} not found.')
            pbar.update()
