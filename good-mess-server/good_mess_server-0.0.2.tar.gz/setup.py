from setuptools import setup, find_packages

setup(name="good_mess_server",
      version="0.0.2",
      description="good_mess_server",
      author="Daniil A.",
      author_email="abyazov2000@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
