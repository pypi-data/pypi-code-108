from setuptools import setup
from io import open


def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()


def requirements():
    with open('requirements.txt', 'r') as req:
        return [r for r in req.read().split("\n") if r]


setup(
    name='response_report',
    version='1.1.1',
    packages=['response_report'],
    url='https://gitlab.com/whiteapfel/response_report',
    license='Mozilla Public License 2.0',
    author='WhiteApfel',
    author_email='white@pfel.ru',
    description='Save the response from the server. This may be needed when debugging.',
    install_requires=requirements(),
    project_urls={
        "Donate": "https://pfel.cc/donate",
        "Telegram": "https://t.me/apfel"
    },
    long_description=read('README.md'),
    long_description_content_type="text/markdown"
)
