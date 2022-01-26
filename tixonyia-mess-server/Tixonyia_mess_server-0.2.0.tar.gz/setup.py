from setuptools import setup, find_packages

setup(name="Tixonyia_mess_server",
      version="0.2.0",
      description="Mess Server",
      author="Vasilev Artem",
      author_email="220220220220@rambler.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
