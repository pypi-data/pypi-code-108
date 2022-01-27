from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='scratchlink',
    version='1.0.1',
    description='ScratchLink is a simple Python Library to get the data of Scratch using the Scratch API. This library is simple to use. This library need no login!',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/Sid72020123/scratchlink/',
    author='Siddhesh Chavan',
    author_email='siddheshchavan2020@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='connect-scratch scratch-api api',
    packages=find_packages(),
    install_requires=['requests']
)
