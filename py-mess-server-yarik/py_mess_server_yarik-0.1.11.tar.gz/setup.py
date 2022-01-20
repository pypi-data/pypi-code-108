from setuptools import setup, find_packages

setup(name="py_mess_server_yarik",
      version="0.1.11",
      description="Mess Server",
      author="Nikolay",
      author_email="nik@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
