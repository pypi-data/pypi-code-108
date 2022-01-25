from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='scratchconnect',
    version='2.4.2',
    description='Python Library to connect Scratch API and much more. This library can show the statistics of Users, Projects, Studios, Forums and also connect and set cloud variables of a project!',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/Sid72020123/scratchconnect/',
    author='Siddhesh Chavan',
    author_email='siddheshchavan2020@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='connect-scratch scratch-api api',
    packages=find_packages(),
    install_requires=['requests', 'websocket-client', 'pyemitter']
)
