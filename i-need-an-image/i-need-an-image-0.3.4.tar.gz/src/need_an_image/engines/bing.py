import random
import json
import logging
from io import BytesIO

import requests
from PIL import Image, UnidentifiedImageError
from bs4 import BeautifulSoup
from jieba import analyse
from need_an_image.utils.decorators import retry_request


class BingImage:

    url = 'https://cn.bing.com/images/search'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'
    }
    _images = []

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_image_source_url(self, response):
        if not self._images:
            soup = BeautifulSoup(response.text, features='lxml')

            image_component = soup.find(id='mmComponent_images_1')
            self._images = image_component.find_all('a', class_='iusc')

        random.shuffle(self._images)
        image = self._images.pop(0)
        metadata = json.loads(image['m'])
        source_url = metadata['murl']

        return source_url

    def get_an_image(self, keyword, max_retry=0, exact=True, allow_pos=()):
        """
        return an Image matching keyword from web
        """
        if not exact:
            keywords = analyse.extract_tags(keyword, allowPOS=allow_pos)
            if not keywords:
                keywords = analyse.extract_tags(keyword)
            keyword = keywords[0]
        self.logger.info(f'Downloading image for keyword: {keyword}.')

        response = self.download_search_page(keyword)

        while max_retry >= 0:

            try:
                source_url = self.get_image_source_url(response)
                if source_url is None:
                    continue
                image_content = self.download_image(source_url)
                image = Image.open(BytesIO(image_content))
                self.clean_image_metadata_cache()
                self.logger.info(f'Download image for keyword: {keyword}, Successfully.')
                return image

            except (UnidentifiedImageError, requests.RequestException):
                self.logger.info(f'Retry downloading image for keyword: {keyword}.')
                max_retry -= 1

        self.clean_image_metadata_cache()
        self.logger.info(f'Failed to download image for keyword: {keyword}.')

    @retry_request(max_retry=2)
    def download_image(self, source_url):
        """
        request picture, return binary data
        """
        response = requests.get(source_url, headers=self.headers, timeout=(3.05, 3))
        return response.content

    def download_search_page(self, keyword):
        """
        Send an image search search_request
        """
        payload = {'q': keyword}
        return requests.get(self.url, params=payload, headers=self.headers, timeout=(3.05, 5))

    def clean_image_metadata_cache(self):
        self._images.clear()
