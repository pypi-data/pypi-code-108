# -*- coding: utf-8 -*-

import glob
from setuptools import setup, find_packages

setup(
    name='chess_classification',
    version='0.0.2',
    url='https://github.com/akuroiwa/chess-classification',
    # # PyPI url
    # download_url='',
    license='GNU/LGPLv3',
    author='Akihiro Kuroiwa',
    author_email='akuroiwa@env-reform.com',
    description='Deep learning in FEN’s win / loss evaluation.',
    # long_description="\n%s" % open('README.md').read(),
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    # python_requires=">=3.8",
    python_requires=">=3.7",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        "Operating System :: OS Independent",
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        # 'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms='any',
    keywords=['classification', 'stockfish', 'transformer', 'bert', 'chess', 'fen', 'pgn'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['chess', 'simpletransformers', 'pandas'],
    entry_points={
        'console_scripts': [
            'genPgn = chess_classification.genPgn:console_script',
            'importPgn = chess_classification.importPgn:console_script'
            ]},
)
