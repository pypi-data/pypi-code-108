# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['echo1_coco_builder']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.14.1,<4.0.0', 'pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'echo1-coco-builder',
    'version': '0.1.5',
    'description': '',
    'long_description': '## Introduction\n`echo1-coco-builder` provides a faster, safer way to build coco formatted data.\n\nSee: https://cocodataset.org/#format-data for more information\n\n## Installation\n```shell\n# If using pip\npip install echo1-coco-builder\n\n# If using poetry\npoetry add echo1-coco-builder\n```\n\n## Example use\n```python\nimport pandas as pd\nfrom echo1_coco_builder.echo1_coco_builder import CocoBuilder\n\n# Open a CSV using pandas\ndf = pd.read_csv("test.csv")\n\n# Initialize the coco builder\ncoco_builder = CocoBuilder()\n\n# For each row in the csv\nfor annotation_id, row in df.iterrows():\n\n    # image_id must be an integer\n    image_id = row["image_name"]\n\n    # image_name must be a string\n    file_name = row["image_name"]\n\n    # image_width and image_height must be an integer\n    image_width = row["image_width"]\n    image_height = row["image_height"]\n\n    # category_id must be an integer\n    category_id = row["category_id"]\n\n    # category_name must be a string\n    category_name = row["category_name"]\n\n    # bbox format: [x,y,width,height]\n    bbox = row["bbox"].split(",")\n\n    # add a new image\n    coco_builder.add_image(image_id, file_name, image_width, image_height)\n\n    # add a new category\n    coco_builder.add_category(category_id, category_name)\n\n    # add a new annotation\n    coco_builder.add_annotation(annotation_id, image_id, category_id, bbox, [], 0, 0)\n\n# add info\ncoco_builder.add_info(2022, "v1.0", "Echo1", "", "https://echo1.io")\n\n# print the data in the coco format as a python object\nprint(coco_builder)\n\n# print the data in the coco format as json\nprint(coco_builder.get())\n\n# save the data in the coco format as json\npython_file = open("example-data.json", "w")\npython_file.write(coco_builder.get())\npython_file.close()\n```',
    'author': 'Michael Mohamed',
    'author_email': 'michael.mohamed@echo1.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/e1-io/echo1-coco-builder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
