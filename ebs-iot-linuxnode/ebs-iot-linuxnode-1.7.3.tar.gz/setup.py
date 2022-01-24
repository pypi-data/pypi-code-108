import setuptools

_requires = [
    'six',
    'setuptools-scm',
    'appdirs',
    'Cython',
    'twisted[tls]',
    'SQLAlchemy',
    'kivy>=1.11.1',
    'kivy-garden',
    'arrow',
    'raspi_system',

    # Node Id
    'netifaces',

    # System
    'ifcfg',

    # BleedImage
    'colorthief',
    
    # HTTP Client
    'treq',

    # Event Manager
    'cached_property',
    'pqueue',

    # Browser
    'selenium',

    # RPi Mediaplayer
    'omxplayer-wrapper',
    'pymediainfo',

    # PdfPlayer
    'pdf2image',

    # Text and Localization
    'hoshi',
]

setuptools.setup(
    name='ebs-iot-linuxnode',
    url='',

    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',

    description='',
    long_description='',

    packages=setuptools.find_packages(),
    package_dir={'ebs.iot.linuxnode': 'ebs/iot/linuxnode'},
    package_data={'ebs.iot.linuxnode': ['images/no-internet.png',
                                        'images/no-server.png']},

    install_requires=_requires,

    setup_requires=['setuptools_scm'],
    use_scm_version=True,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
    ],
)
