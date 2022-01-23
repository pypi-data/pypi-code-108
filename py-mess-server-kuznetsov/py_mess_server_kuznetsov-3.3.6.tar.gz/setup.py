from setuptools import setup, find_packages

setup(name="py_mess_server_kuznetsov",
      version="3.3.6",
      description="Mess Server",
      author="Sergey Kuznetsov",
      author_email="ksn1974@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      # scripts=['server/server_run']
      )

