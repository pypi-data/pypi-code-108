from setuptools import setup, find_packages

setup(name="selses_messanger_client",
      version="0.0.2",
      description="Mess Client",
      author="SomeoneElse",
      author_email="fatal.critical.error@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
