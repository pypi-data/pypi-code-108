import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='py-ampq-websocket-server',
    version='0.1.7',
    author='Smirnov.EV',
    author_email='knyazz@gmail.com',
    description='python websockets server using ampq',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/knyazz/py-ampq-websocket-server',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta'
    ],
    install_requires=[
        'pika>=1.2.0',
        'redis>=2.9.1',
        'websockets>=10.1',
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9"
)
