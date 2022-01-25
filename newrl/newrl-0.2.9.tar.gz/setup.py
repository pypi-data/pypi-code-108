from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
  name = 'newrl',
  packages = ['newrl'],
  version = '0.2.9',
  license='MIT',
  description = 'Python SDK for Newrl blockchain',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Kousthub Raja',
  author_email = 'kousthub@asqi.in',
  url = 'https://github.com/asqi/newrl',
  download_url = 'https://github.com/asqisys/newrl-py/archive/refs/tags/v_02.tar.gz',
  keywords = ['newrl', 'blockchain', 'client'],
  install_requires=[
    'requests',
    'ecdsa',
    'pycryptodome',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)