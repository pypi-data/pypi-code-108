# coding=utf-8

from setuptools import setup, find_packages


def readme():
    with open('./README.md', encoding="utf-8") as f:
        _long_description = f.read()
        return _long_description


setup(
    name='BusyBox',
    version="0.8.0",
    description=(
        """Service Inject For MVC
        
            params inject
            object reset
        """
    ),
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords=['inject', 'depend', 'invoke', 'BusyBox'],
    author='Jansen Leo',
    author_email='2835347017@qq.com',
    maintainer='Jansen Leo',
    maintainer_email='2835347017@qq.com',
    license='MIT License',
    packages=['BusyBox'],
    platforms=["linux", 'windows'],
    url='https://github.com/AngelovLee/BusyBox',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
    ]
)