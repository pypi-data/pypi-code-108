from setuptools import setup, find_packages

setup(name="py_net_chat",
      version="0.3.0",
      description="NetChat",
      author="NetChatAdmin",
      author_email="ncha@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
