from setuptools import setup, find_packages
from pathlib import Path

# read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

setup(
    name='improc',
    version='0.1.0',
    license='gpl-2.0',
    description='TODO',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jiří Szkandera',
    author_email='jirik.sz@gmail.com',
    packages=find_packages('src'),
    install_requires=[
        'numpy',
        'opencv-python',
        'matplotlib',
        'pyyaml',
        'scikit-spatial',
        'pytesseract',
        'google-cloud-vision',
    ],
    extras_require={
        'interactive': [
            'ipython',
            'ipywidgets',
        ]
    },
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
)
