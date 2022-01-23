import pathlib

import pkg_resources
import setuptools

with open('readme.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='Deep Learning Plus',
    version='0.0.8',
    author='Greenfrogs',
    author_email='5961364+greenfrogs@users.noreply.github.com',
    description='A collection of Python packages designed for the Python 3.9 for when you only want 1 import',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/greenfrogs/DeepLearningPlus',
    license='Apache License 2.0',
    install_requires=[
        'tqdm==4.62.3',
        'h5py==3.6.0',
        'matplotlib==3.5.1',
        'opencv-python==4.5.4.60',
        'scipy==1.7.3',
        'Pillow==8.4.0',
        'pandas==1.3.5',
        'scikit-image==0.19.1',
        'scikit-learn==1.0.2',
        'ImageHash==4.2.1',
        'psutil==5.9.0'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    python_requires='==3.9.*',
)
