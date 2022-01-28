from setuptools import setup, find_packages

setup(
    name='lEmoji',
    version='0.2.3',
    keywords=['emoji'],
    description='emoji list for all version based on unicode.org',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license='MIT Licence',
    url='https://github.com/lqj679ssn/lemoji',
    author='Jyonn Liu',
    author_email='i@6-79.cn',
    platforms='any',
    packages=find_packages(),
    install_requires=[],
)
