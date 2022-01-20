import os
import hashlib
from setuptools import setup, find_packages
from improve.version import version

__packages__=['improve'
              ]
print(__packages__)


print(version)
package_name = 'ls2_picture'
entry = 'ls2_picture=improve.interface:interface'
setup(
    name = package_name,
    version = version,
    description = "Look spot II picture improvement",
    author = 'Laipac',
    author_email = 'feng.gao@laipac.com',
    url = 'https://github.com/gxfca/gitTest',
    packages = __packages__,
#    package_dir ={'spoitii':'spotii'},
    package_data={
        'improve':[
                    '*.ui',
                    '*.txt',
                  ],
                  },
    entry_points={
    'console_scripts': [
        entry,
    ],
    },
    )
