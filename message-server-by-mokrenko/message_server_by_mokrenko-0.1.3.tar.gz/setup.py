from setuptools import setup, find_packages

setup(name="message_server_by_mokrenko",
      version="0.1.3",
      description="Message Server Package",
      author="Vladimir Mokrenko",
      author_email="v.v.mokrenko@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
