from setuptools import setup
import MicroserviceLibSender

setup(
    name="MicroserviceLibSender",
    version=MicroserviceLibSender.__version__,
    author='Vyacheslav Anzhiganov',
    author_email='hello@anzhiganov.com',
    url="https://stackwebservices.com",
    packages=[
        'MicroserviceLibSender',
    ],
    package_data={
    },
    scripts=[
    ],
    install_requires=[
        'requests==2.27.1',
    ]
)
