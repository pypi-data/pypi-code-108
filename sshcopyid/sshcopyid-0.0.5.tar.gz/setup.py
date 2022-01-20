from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='sshcopyid',
    version='0.0.5',
    description='Simplified replication of the linux ' +
    'ssh-copy-id cli for windows',
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Meena (Menas) Erian',
    author_email="menas@portacode.com",
    # python_requires=[],
    url='https://github.com/meena-erian/ssh-copy-id',
    scripts=['cli/cli.py'],
    entry_points={
        'console_scripts': ['ssh-copy-id=cli:main'],
    },
    install_requires=[],
    include_package_data=True,
    license='LICENSE',
    classifiers=[
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Networking'
    ]
)
