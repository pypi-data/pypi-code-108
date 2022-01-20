from setuptools import setup, find_packages

setup(name="py_mess_server",
      version="0.2.1",
      description="Mess Server",
      author="Ivan Ivanov",
      author_email="iv.iv@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
