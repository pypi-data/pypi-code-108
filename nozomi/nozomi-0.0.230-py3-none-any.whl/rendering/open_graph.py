
"""
Nozomi
Open Graph Module
Author: hugh@blinkybeach.com
"""

from typing import Dict, Any


class OpenGraph:
    """OpenGraph information for inclusion in a page header."""
    _HTTPS = 'https://'
    _DEFAULT_TYPE = 'website'

    def __init__(self, url, title, description, image):

        assert isinstance(url, str)
        assert isinstance(title, str)
        assert isinstance(description, str)
        assert isinstance(image, str)
        assert url[:len(self._HTTPS)] == self._HTTPS
        assert image[:len(self._HTTPS)] == self._HTTPS

        self._url = url
        self._title = title
        self._description = description
        self._image = image

        return

    def as_dict(self) -> Dict[str, Any]:
        """
        Return OpenGraph contents as a JSON
        serialsable dictionary
        """
        data = {
            'url': self._url,
            'title': self._title,
            'description': self._description,
            'image': self._image,
            'type': self._DEFAULT_TYPE
        }
        return data
