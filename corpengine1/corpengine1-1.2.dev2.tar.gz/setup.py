from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

changelog = 'v1.2.dev2\n\nAdded corpengine1.Rectangle functionality for the isCollidingWithMouse() method in UserInputService.'

setup(
    name='corpengine1',
    version='1.2.dev2',
    description='Fast, Organized, Object-Oriented Python Game Development',
    long_description='github repository: https://github.com/corpengine/corpengine' + '\n\nChangelog:\n'+changelog,
    url='https://corpengine.github.io/',
    license='MIT',
    classifiers=classifiers,
    keywords='corpengine',
    packages=find_packages(),
    install_requires=['easygui', 'pygame']
)