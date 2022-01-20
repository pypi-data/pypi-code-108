import pathlib
import re

from setuptools import setup

WORK_DIR = pathlib.Path(__file__).parent


def get_description():
    """
    Read full description from 'README.rst'
    :return: description
    :rtype: str
    """
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


def get_version():
    """
    Read version
    :return: str
    """
    txt = (WORK_DIR / 'hentai_chan_api' / '__init__.py').read_text('utf-8')
    try:
        return re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


setup(
    name='hentai_chan_api',
    version=get_version(),
    packages=['hentai_chan_api'],
    install_requires=['requests', 'beautifulsoup4'],
    url='https://github.com/JKearnsl/HentaiChanApi',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    author='JKearnsl',
    author_email='pooolg@hotmail.com',
    description='Wrapper over https://hentaichan.live | There is also an asynchronous version, go to github',
    long_description=get_description(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
