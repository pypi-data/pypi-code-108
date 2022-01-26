import setuptools
import sof_utils

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    requirements = fh.readlines()
requirements = [line.strip('\n') for line in requirements]

setuptools.setup(
    name="sof_utils",
    version=sof_utils.__version__,
    author="Stefan Reinhold",
    description="Small utilities to aid working with the SOF dataset",
    author_email="stefan@sreinhold.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ithron/SOF-Utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=[
        'bin/sof-dicom-meta',
        'bin/sof-dicom-corrupted',
        'bin/sof-export-images',
        'bin/sof-convert-labels',
        'bin/sof-convert-tfds',
        'bin/sof-detect-keypoints',
        'bin/sof-keypoint-outliers'
    ],
    install_requires=requirements
)
