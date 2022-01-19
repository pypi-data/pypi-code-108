from setuptools import setup, find_packages

setup(name="python_messngr_srvr",
      version="0.1.0",
      description="Messenger Server",
      author="Stepan Rashevskii",
      author_email="rashevskii@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
