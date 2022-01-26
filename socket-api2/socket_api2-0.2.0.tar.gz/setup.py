from setuptools import setup, find_packages, version

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name="socket_api2",
    version="0.2.0",
    description="Socket Api 2 creates the best connection between a server and client/clients, and its compatible with ngrok (pyngrok)",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    author='Da4ndo',
    author_email = 'da4ndo0@gmail.com',
    License="MIT",
    classifiers=classifiers,
    keywords=['socket_api2', 'socket', 'socket_api', 'socket api', 'socket api 2'],
    packages=find_packages(),
    install_requires=['pyngrok', 'colorama']
)