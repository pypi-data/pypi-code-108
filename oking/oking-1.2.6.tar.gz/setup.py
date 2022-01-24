from setuptools import setup, find_packages
from os import path


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()


def save_version(v: str):
    f = open('version.txt', 'w')
    f.write(f'\tOking {v} - Openk Tecnologia')
    f.close()


version = '1.2.6'
save_version(version)
setup(
    name="oking",
    version=version,
    author="Openk Tecnologia",
    author_email="<suporte.b2c@openk.com.br>",
    description='Pacote de integração de produtos, preço, estoque e pedidos com o sistema OkVendas da Openk',
    long_description_content_type="text/markdown",
    long_description=read('README.md'),
    packages=find_packages(include=['src', 'src.*']),
    install_requires=['mysql-connector-python',
                      'schedule',
                      'requests',
                      'configparser',
                      'logger',
                      'cx-Oracle',
                      'jsonpickle',
                      'pyodbc'],
    keywords=['python', 'oking', 'openk', 'okvendas', 'ok'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        # "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'console_scripts': ['oking=src.__main__:main']
    }
)
