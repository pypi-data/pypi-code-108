from setuptools import setup, find_packages

setup(name="DBnPYQT_mess_server",
      version="0.0.1",
      description="DBnPYQT_mess_server",
      author="Aleksandr Sharov",
      author_email="ssh7@bk.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
