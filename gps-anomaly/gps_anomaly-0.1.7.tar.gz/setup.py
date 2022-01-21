# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gps_anomaly']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'gps-anomaly',
    'version': '0.1.7',
    'description': 'Detecet and Remove GPS anomalies points',
    'long_description': '# GPS anomaly detection\n\n```bash\npip install gps-anomaly\n``` \n\n### Usage\n```python\nfrom gps_anomaly.detector import Anomaly\n\nanomaly = Anomaly()\npoints = [{\n        "Latitude": 22.32689719997222,\n        "Longitude": 11.49237269997222,\n        "CaptureTime": "2021_11_18_15_22_52_000",\n        "Altitude": 7.386,\n        "SequenceUUID": "1490d87b-d5ba-4df3-b354-c01e7acaae29",\n        "Heading": 195.9560290711052,\n        "Orientation": 3,\n        "DeviceMake": "GoPro Max",\n        "DeviceModel": "GOPRO",\n        "ImageSize": "2704x2028",\n        "FoV": 100.4,\n        "PhotoUUID": "21887915-e624-4246-b7e9-695b44fb6442",\n        "filename": "GPAG8025.JPG",\n        "path": ""\n    },\n    {\n        "Latitude": 22.32654149997222,\n        "Longitude": 11.4922393,\n        "CaptureTime": "2021_11_18_15_22_53_000",\n        "Altitude": 6.029,\n        "SequenceUUID": "1490d87b-d5ba-4df3-b354-c01e7acaae29",\n        "Orientation": 3,\n        "DeviceMake": "GoPro Max",\n        "DeviceModel": "GOPRO",\n        "ImageSize": "2704x2028",\n        "FoV": 100.4,\n        "PhotoUUID": "ff612ec5-9479-473a-925b-8336af0b1e1f",\n        "filename": "GPAG8026.JPG",\n        "path": ""\n    },\n    {\n        "Information": {\n            "total_images": 2,\n            "processed_images": 2,\n            "failed_images": 0,\n            "duplicated_images": 0,\n            "id": "8323ff0a01fe49d1b55e610279f62828"\n        }\n    }\n]\nprint(anomaly.anomaly_detector(frames=points))\n```\n\n### Output\n```bash\n[\n    {\n        "Information": {\n            "total_images": 2,\n            "processed_images": 2,\n            "failed_images": 0,\n            "duplicated_images": 0,\n            "id": "8323ff0a01fe49d1b55e610279f62828"\n        }\n    }\n]\n```',
    'author': 'mcv_',
    'author_email': 'murat@visiosoft.com.tr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
