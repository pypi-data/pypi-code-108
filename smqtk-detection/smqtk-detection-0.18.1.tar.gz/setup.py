# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smqtk_detection',
 'smqtk_detection.impls',
 'smqtk_detection.impls.detect_image_objects',
 'smqtk_detection.impls.detection_element',
 'smqtk_detection.interfaces',
 'smqtk_detection.utils']

package_data = \
{'': ['*']}

install_requires = \
['smqtk-classifier>=0.19.0',
 'smqtk-core>=0.18.0',
 'smqtk-dataprovider>=0.16.0',
 'smqtk-image-io>=0.16.2']

extras_require = \
{'centernet': ['torch>=1.10.0,<2.0.0',
               'opencv-python>=4.5.2.0,<4.6.0.0',
               'numba>=0.53.0,<0.54.0'],
 'torch': ['torch>=1.10.0,<2.0.0', 'torchvision>=0.11.1,<0.12.0']}

entry_points = \
{'smqtk_plugins': ['smqtk_detection.impls.detect_image_objects.centernet = '
                   'smqtk_detection.impls.detect_image_objects.centernet',
                   'smqtk_detection.impls.detect_image_objects.random_detector '
                   '= '
                   'smqtk_detection.impls.detect_image_objects.random_detector',
                   'smqtk_detection.impls.detect_image_objects.resnet_frcnn = '
                   'smqtk_detection.impls.detect_image_objects.resnet_frcnn',
                   'smqtk_detection.impls.detection_element.memory = '
                   'smqtk_detection.impls.detection_element.memory']}

setup_kwargs = {
    'name': 'smqtk-detection',
    'version': '0.18.1',
    'description': 'Algorithms, data structures and utilities around performing detection of inputs',
    'long_description': '## Intent\n\n## Documentation\n\nDocumentation for SMQTK is maintained at\n[ReadtheDocs](https://smqtk.readthedocs.org), including\n[build instructions](https://smqtk.readthedocs.io/en/latest/installation.html)\nand [examples](https://smqtk.readthedocs.org/en/latest/examples/overview.html).\n\nAlternatively, you can build the sphinx documentation locally for the most\nup-to-date reference (see also: [Building the Documentation](\nhttps://smqtk.readthedocs.io/en/latest/installation.html#building-the-documentation)):\n```bash\n# Navigate to the documentation root.\ncd docs\n# Install dependencies and build Sphinx docs.\npip install -r readthedocs-reqs.txt\nmake html\n# Open in your favorite browser!\nfirefox _build/html/index.html\n```\n',
    'author': 'Kitware, Inc.',
    'author_email': 'smqtk-developers@kitware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kitware/SMQTK-Detection',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<3.10',
}


setup(**setup_kwargs)
