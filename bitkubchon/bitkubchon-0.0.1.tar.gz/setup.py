from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='bitkubchon',
    version='0.0.1',
    description='Test',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author='chon',
    license='chon',
    scripts=[],
    keywords='chon',
    packages=['bitkubchon'],
    install_requires=['requests'],
)
