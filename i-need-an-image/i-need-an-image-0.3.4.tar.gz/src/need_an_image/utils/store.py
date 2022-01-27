import os.path
from uuid import uuid4


def save_image(image, save_to='.'):
    """
    Save image to local dick
    """
    suffix = '.jpg'

    if image.mode == 'P':
        image = image.convert('RGBA')

    if image.mode == 'RGBA':
        suffix = '.png'

    filename = uuid4().hex + suffix

    if not os.path.isdir(save_to):
        os.makedirs(save_to)
    filename = os.path.join(save_to, filename)

    image.save(filename)
    return filename
