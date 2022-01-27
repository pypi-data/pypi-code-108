
import logging
import sys
from tawnyapi.vision.apitypes import ImageAnnotationFeatures
from typing import List
from pprint import pprint
import json
import typer

from .client import TawnyVisionApiClient
from .apitypes import ImageAnnotationFeatures

app = typer.Typer()


def _setup_logging(level=logging.DEBUG):
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


logger = logging.getLogger(__name__)


@app.command()
def hello():
    print('Hello from TAWNY!')


@app.command()
def analyze(
        image: List[str] = [],
        maxresults: int = 1,
        resize: int = None,
        apiurl: str = 'https://vision.tawnyapis.com',
        apikey: str = None,
        uselocalfacedetection: bool = False,
        uselocalfaceembedding: bool = False,
        feature: List[ImageAnnotationFeatures] = [
            ImageAnnotationFeatures.FACE_DETECTION,
            ImageAnnotationFeatures.FACE_EMOTION
        ]
):
    """
    Sends a request to the TAWNY Vision API. You can provide --image more than
    once to send several images in one request.
    """

    if apiurl is None:
        print('ERROR: You have to provide the --apiurl argument.')
        return

    if apikey is None:
        print('ERROR: You have to provide the --apikey argument.')
        return

    client = TawnyVisionApiClient(
        api_url=apiurl,
        api_key=apikey,
        use_local_face_detection=uselocalfacedetection,
        use_local_face_embedding=uselocalfaceembedding
    )
    result = client.analyze_images_from_paths(
        image_paths=image,
        max_results=maxresults,
        resize=resize,
        features=feature
    )
    result = json.dumps(result)
    print(result)


if __name__ == "__main__":
    _setup_logging()
    app()
