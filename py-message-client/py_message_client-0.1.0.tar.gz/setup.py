from setuptools import setup, find_packages

setup(name="py_message_client",
      version="0.1.0",
      description="Message Client",
      author="User",
      author_email="shtyrov89@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
