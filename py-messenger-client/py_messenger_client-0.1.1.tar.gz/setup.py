from setuptools import setup, find_packages

setup(name="py_messenger_client",
      version="0.1.1",
      description="messenger client",
      author="Murij Kate",
      author_email="murij.kat@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['client/client_run']
      )
