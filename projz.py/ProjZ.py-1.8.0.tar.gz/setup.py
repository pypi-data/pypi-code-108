from setuptools import setup, find_packages

requirements = [
    "httpx[all]",
    "typing",
    "websocket-client", 
    "ujson",
    "aiofiles",
    "h2"
]

setup(name = "ProjZ.py",
      version = "1.8.0",
      description = "Library for project z",
      packages = find_packages(),
      author_email = "ktoya170214@gmail.com",
      install_requires = requirements,
      zip_safe = False)