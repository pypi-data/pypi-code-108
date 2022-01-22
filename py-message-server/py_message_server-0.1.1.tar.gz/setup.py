from setuptools import setup, find_packages

setup(name="py_message_server",
      version="0.1.1",
      description="Message Server",
      author="User",
      author_email="shtyrov89@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run']
      )
