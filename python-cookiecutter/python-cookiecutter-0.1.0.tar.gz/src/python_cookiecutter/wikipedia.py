"""Client for the Wikipedia REST API, version 1."""
from dataclasses import dataclass

import click
import desert
import marshmallow
import requests


# Points to the REST API of the English Wikipedia () /page/random/summary) endpoint,
# which returns the summary of a random Wikipedia article.
API_URL: str = "https://{language}.wikipedia.org/api/rest_v1/page/random/summary"


@dataclass
class Page:
    """Page resource.

    Attributes:
        title: The title of the Wikipedia page.
        extract: A plain text summary.
    """

    title: str
    extract: str


# Generate a schema from the Page dataclass. Tell marshmallow to ignore unknown fields.
schema = desert.schema(Page, meta={"unknown": marshmallow.EXCLUDE})


def random_page(language: str = "en") -> Page:
    """Return a random page.

    Performs a GET request to the /page/random/summary endpoint.

    Args:
        language: The Wikipedia language edition. By default, the English
            Wikipedia is used ("en").

    Returns:
        A page resource.

    Raises:
        ClickException: The HTTP request failed or the HTTP response
            contained an invalid body.

    Example:
        >>> from hypermodern_python import wikipedia
        >>> page = wikipedia.random_page(language="en")
        >>> bool(page.title)
        True
    """
    url: str = API_URL.format(language=language)

    try:
        # Send a HTTP GET request to the Wikipedia API.
        with requests.get(url) as response:
            # Check the HTTP status code and raise an exception if it signals an error.
            response.raise_for_status()
            # Get the resource data.
            data = response.json()
            return schema.load(data)
    except (requests.RequestException, marshmallow.ValidationError) as error:
        message: str = str(error)
        raise click.ClickException(message) from error
