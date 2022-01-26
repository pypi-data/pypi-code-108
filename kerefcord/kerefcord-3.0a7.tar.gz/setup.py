from setuptools import setup
import re

requirements = []

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

version = "3.0a7"

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.rst') as f:
    readme = f.read()

extras_require = {
    'voice': ['PyNaCl>=1.3.0,<1.5'],
    'docs': [
        'sphinx==4.0.2',
        'sphinxcontrib_trio==1.1.2',
        'sphinxcontrib-websupport',
    ],
    'speed': [
        'orjson>=3.5.4',
    ]
}

packages = [
    'kerefcord',
    'kerefcord.types',
    'kerefcord.ui',
    'kerefcord.webhook',
    'kerefcord.ext.commands',
    'kerefcord.ext.tasks',
]

setup(name='kerefcord',
      author='Keref',
      url='https://github.com/Kerefkerefcord/kerefcord.py',
      project_urls={
        "Documentation": "https://kerefcordpy.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/Kerefkerefcord/discrap.py/issues",
      },
      version="3.0a7",
      packages=packages,
      license='MIT',
      description='A Python wrapper for the kerefcord API',
      long_description=readme,
      long_description_content_type="text/x-rst",
      include_package_data=True,
      install_requires=requirements,
      extras_require=extras_require,
      python_requires='>=3.8.0',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
      ]
)
