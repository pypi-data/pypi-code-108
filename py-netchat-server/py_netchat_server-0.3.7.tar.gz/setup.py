from setuptools import setup, find_packages

setup(name="py_netchat_server",
      version="0.3.7",
      description="NetChat Server",
      author="Ncha",
      author_email="ncha@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
