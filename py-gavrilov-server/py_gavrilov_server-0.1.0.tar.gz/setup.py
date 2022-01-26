from setuptools import setup, find_packages

setup(name="py_gavrilov_server",
      version="0.1.0",
      description="Messeger Server",
      author="Gavrilov Artemiy",
      author_email="voodoo06.89@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
