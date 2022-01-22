from setuptools import setup, find_packages

setup(name="the_me_mess_server",
      version="0.0.1",
      description="the_me_mess_server",
      author="the_me",
      author_email="the_me@live.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )