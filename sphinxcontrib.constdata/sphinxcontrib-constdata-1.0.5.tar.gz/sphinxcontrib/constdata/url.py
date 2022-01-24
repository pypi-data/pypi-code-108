from typing import List, Tuple
from urllib.parse import parse_qsl, urlparse

from sphinxcontrib.constdata.utils import ConstdataError


class Url:
    """
    Convinient flatfile URL reading. URL appears in

    - :constdata:label:`url`
    - :constdata:link:`url`
    - :constdata:link:`title <url>`
    """

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url_raw = url
        self.url_parsed = urlparse(self.url_raw)
        self.qs_raw = self.url_parsed.query
        # without keep_blank_values=True, parse_qsl discard qs like "someId"
        self.qs_parsed: List[Tuple[str, str]] = parse_qsl(
            self.qs_raw, keep_blank_values=True
        )

    def get_id(self) -> str:
        """
        Extract ID from URL. Eg., from URL ``foo.csv?someid`` returns ``someid``.

        :raise ConstdataError: on invalid ID in URL.
        """
        if (
            (len(self.qs_parsed) == 0)
            or (len(self.qs_parsed) > 1)  # no QS
            or (len(self.qs_parsed) == 1 and self.qs_parsed[0][1] != "")  # more than 1
        ):  # 1 but not empty

            raise ConstdataError(
                f"Invalid or not specified ID in URL querystring. URL is '{self.url_raw}', querystring is "
                f"'{self.qs_raw}'. Correct URL is, e.g. 'foo.csv?someId'."
            )

        return self.qs_parsed[0][0]

    def get_rel_path(self) -> str:
        """
        Extract relative path from URL. E.g., from URL ``foo.csv?someid`` path is ``foo.csv``
        """
        return self.url_parsed.path
