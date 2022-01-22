from setuptools import setup
setup(
        name = 'comicapi',
        version = '2.2.1',
        description = 'Comic archive (cbr/cbz/cbt) and metadata utilities. Extracted from the comictagger project.',
        author = 'Iris W',
        maintainer = "@OzzieIsaacs",
        packages = ['comicapi'],
        install_requires = ['natsort>=3.5.2'],
        extras_require = {
            'CBR': ['rarfile==2.7']
        },
        python_requires = '>=3.0.0',
        url = 'https://github.com/OzzieIsaacs/comicapi',
        classifiers = [
                "Programming Language :: Python :: 3",
                'License :: OSI Approved :: Apache Software License',
                "Operating System :: OS Independent",
        ]
)
