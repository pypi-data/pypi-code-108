from setuptools import setup, find_packages

setup(name="simple_mess_server",
      version="0.1.0",
      description="Messenger Client",
      author="Kirillova V.",
      author_email="victmanio@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
