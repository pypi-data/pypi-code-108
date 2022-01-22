from setuptools import setup, find_packages

setup(name="py_messenger_server",
      version="0.1.5",
      description="messenger server",
      author="Murij Kate",
      author_email="murij.kat@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
