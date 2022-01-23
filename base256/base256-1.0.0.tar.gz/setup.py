from setuptools import setup, find_packages
setup(
    name='base256',
    version='1.0.0',
    license='MIT',
    author='Elisha Hollander',
    author_email='just4now666666@gmail.com',
    description="When base64 just isn't enough",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/donno2048/base256',
    project_urls={
        'Documentation': 'https://github.com/donno2048/base256#readme',
        'Bug Reports': 'https://github.com/donno2048/base256/issues',
        'Source Code': 'https://github.com/donno2048/base256',
    },
    python_requires='>=3.0',
    packages=find_packages(),
    install_requires=['prompt_toolkit'],
    entry_points={ 'console_scripts': [ 'base256=base256.__main__:main' ] }
)
