from setuptools import setup, find_packages

classifiers = [ 
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
    name='dj2e',
    version='0.0.3',
    description='Parses json embeds to python embed objects.',
    Long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://die.ooo',
    author='xevaly',
    author_email='xevaly@die.ooo',
    License='MIT',
    classifiers=classifiers,
    keywords='discord embed',
    packages=find_packages(),
    install_requires=['discord.py==1.7.3']
)