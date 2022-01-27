# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/dg_util'}

packages = \
['face_parsing',
 'face_parsing.cmd',
 'image_preprocessing',
 'rembg',
 'rembg.cmd',
 'rembg.u2net']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'dlib>=19.22.1,<20.0.0',
 'filetype>=1.0.7,<2.0.0',
 'flask>=1.1.2,<2.0.0',
 'imutils>=0.5.4,<0.6.0',
 'numpy>=1.21.4,<2.0.0',
 'opencv-python>=4.5.4,<5.0.0',
 'pymatting>=1.1.1,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'scikit-image>=0.17.2,<0.18.0',
 'scipy>=1.5.4,<2.0.0',
 'torch>=1.10.0,<2.0.0',
 'torchaudio>=0.10.0,<0.11.0',
 'torchvision>=0.11.1,<0.12.0',
 'tqdm>=4.62.3,<5.0.0',
 'waitress>=1.4.4,<2.0.0']

entry_points = \
{'console_scripts': ['parsing = face_parsing.cmd.cli:main',
                     'rembg = rembg.cmd.cli:main']}

setup_kwargs = {
    'name': 'dg-util',
    'version': '0.0.31',
    'description': 'commom tools',
    'long_description': '# Package dg_util \nv 0.0.15\n\nPackage dg_util consists of different interface of commonly used basic functions in development process to help reduce redoundancy and keep your codes clean. More features will be updated in future.\n* Install: \n\n```bash\npip install dg_util\n```\n\n* Uninstall: \n\n```bash\npip uninstall dg_util\n```\n\n## Features\n### Image Reprocessing\nCrop face images with landmark.\n1. crop_image\n2. crop_image_from_path\n\n### Face Parsing\nGenreate face parsing with BiSeNet。\n1. parsing_face\n2. parsing_faces\n\n### Rembg\nRemove background.\n1. bg.move',
    'author': 'DataGrid',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
