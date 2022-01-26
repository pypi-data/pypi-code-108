from distutils.core import setup

setup(
  name="arweave-client-python",
  packages = ['arweave'], # this must be the same as the name above
  version="1.0.15.dev0",
  description="Client interface for sending transactions on the Arweave permaweb",
  author="George Omosun E.",
  author_email="george@blacheinc.com",
  url="https://github.com/george-omosun-e/arweave-python-client",
  download_url="https://github.com/george-omosun-e/arweave-python-client",
  keywords=['arweave', 'crypto', 'python'],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  install_requires=[
    'arrow',
    'python-jose',
    'pynacl',
    'pycryptodome',
    'cryptography',
    'requests',
    'psutil'
  ],
)
