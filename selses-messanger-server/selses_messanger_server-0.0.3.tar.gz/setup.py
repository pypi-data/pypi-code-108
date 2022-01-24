from setuptools import setup, find_packages

setup(name="selses_messanger_server",
      version="0.0.3",
      description="Mess Server",
      author="SomeoneElse",
      author_email="fatal.critical.error@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
