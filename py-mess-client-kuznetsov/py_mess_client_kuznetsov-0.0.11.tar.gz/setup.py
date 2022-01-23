from setuptools import setup, find_packages

setup(name="py_mess_client_kuznetsov",
      version="0.0.11",
      description="Mess Client",
      author="Sergey Kuznetsov",
      author_email="ksn1974@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['client/client_run']
      )
