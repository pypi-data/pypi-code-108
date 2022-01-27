# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fimage']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.0.0,<9.0.0', 'numpy>=1.21.4,<2.0.0', 'opencv-python>=4.5.5,<5.0.0']

setup_kwargs = {
    'name': 'fimage',
    'version': '0.2.2',
    'description': 'A Python module to create and apply filters to images.',
    'long_description': '# FImage\n\nA Python module to apply and create multiples filters to images.\n\nYou need to be using Python 3.7 or greater to be able to use **FImage**.\n\n## Installation\n```python\npip install fimage\n```\n\n## Example\n\n### A Simple filter\n\nCreate a file `app.py`  with:\n\n```python\nfrom fimage import FImage\nfrom fimage.filters import Sepia\n\n\ndef main():\n    # replace \'my_picture.jpg\' with the path to your image\n    image = FImage(\'my_picture.jpg\')\n\n    # apply the Sepia filter to the image\n    image.apply(Sepia(90))\n\n    # save the image with the applied filter\n    image.save(\'my_picture_sepia.jpg\')\n\n\nif __name__ == "__main__":\n    main()\n```\n\nNow, just run it :\n\n```python\npython app.py\n```\n\nThis is `my_picture.jpg` before the filter was applied\n\n<img alt="my_picture.jpg" src="examples/img/my_picture.jpg" width="400" height="500">\n\nAnd this is how new image `my_picture_sepia.jpg` looks like after the filter was applied\n\n<img alt="my_picture_sepia.jpg" src="examples/img/my_picture_sepia.jpg" width="400" height="500">\n\n**Note**:  *90 represents the adjustment value we want to use for applying a sepia tone to this picture, lower values will result an image with less sepia tone while higher values will give us an image with a notorious sepia tone.*\n\nMost of the filters **FImage** offers will need an adjustment value to be passed.\n\n### Applying multiple filters\n\n**FImage** offers more filters besides the Sepia one, even you can combine multiples filters to give a better look to your picture.\n\nModify the file `app.py` to import more filters from **FImage**\n\n```python\nfrom fimage import FImage\nfrom fimage.filters import Contrast, Brightness, Saturation\n\n\ndef main():\n    image = FImage(\'my_picture.jpg\')\n\n    # apply the mutiple filters to the image\n    image.apply(\n        Saturation(20),\n        Contrast(25),\n        Brightness(15)\n    )\n\n    # save the image with the applied filter\n    image.save(\'my_picture_mixed.jpg\')\n\n\nif __name__ == "__main__":\n    main()\n```\n\nWe run it by\n\n```python\npython app.py\n```\n\nAnd our new `my_picture_mixed.jpg` looks like\n\n<img alt="my_picture_mixed.jpg" src="examples/img/my_picture_mixed.jpg" width="400" height="500">\n\nThe order in which the filters are passed to the `apply` function matters, this is because the filters are applied in a sequential manner, so the next filter will be applied over the resultant image from the previous one.\n\nCurrently **FImage** supports the following filters:\n- **FillColor**\n- **Sepia**\n- **Contrast**\n- **Brightness**\n- **Saturation**\n- **Vibrance**\n- **Grayscale**\n- **Hue**\n- **Colorize**\n- **Invert**\n- **Gamma**\n- **Noise**\n- **Clip**\n- **Exposure**\n\n### Presets\n\nPresets are just the combinations of multiple filters with already defined adjustment values.\n\nLet’s change our `app.py` one more time to use the Presets\n```python\nfrom fimage import FImage\nfrom fimage.presets import SinCity\n\n\ndef main():\n    # replace \'my_picture.jpg\' with the path to your image\n    image = FImage(\'my_picture.jpg\')\n\n    # apply the SinCity preset to the image\n    image.apply(SinCity())\n\n    # save the image with the applied preset\n    image.save(\'my_picture_sincity.jpg\')\n\n\nif __name__ == "__main__":\n    main()\n```\n\n After we run it, we get our new  `my_picture_sincity.jpg`\n\n<img alt="my_picture_sincity.jpg" src="examples/img/my_picture_sincity.jpg" width="400" height="500">\n\nCurrently supported Presets:\n- **SinCity**\n- **OrangePeel**\n- **Love**\n\n### Custom Presets\nIf you like the look your picture got after testing different filters and want to store this combination for applying it to more pictures, you can create your own Preset by just extending the `Preset` Class and specifying these filters and their adjust values in it.\n\nIn our `app.py` let’s do\n\n```python\nfrom fimage import FImage\nfrom fimage.presets import Preset\nfrom fimage.filters import Contrast, Brightness, Saturation\n\n\n# Create my custom preset and specify the filters to apply\nclass MyOwnPreset(Preset):\n    filters = [\n        Contrast(30),\n        Saturation(50),\n        Brightness(10),\n    ]\n\n\ndef main():\n    # replace \'my_picture.jpg\' with the path to your image\n    image = FImage(\'my_picture.jpg\')\n\n    # apply MyOwnPreset to the image\n    image.apply(MyOwnPreset())\n\n    # save the image with the applied preset\n    image.save(\'my_picture_custom.jpg\')\n\n\nif __name__ == "__main__":\n    main()\n```\n\nThe new `my_picture_custom.jpg`\n\n<img alt="my_picture_custom.jpg" src="examples/img/my_picture_custom.jpg" width="400" height="500">\n\nNow, in this way `MyOwnPreset` has the combination of filters you like and you can use to modify more pictures.',
    'author': 'Jordan Jimenez',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jordandjp/fimage',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
