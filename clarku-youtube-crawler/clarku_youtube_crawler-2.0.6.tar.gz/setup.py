# update version number
# python setup.py sdist bdist_wheel
# twine upload --repository pypi dist/*
# or twine upload --repository-url https://pypi.org/project/clarku-youtube-crawler/ dist/*
# username: shuoniu


# To check packages: twine check dist/*

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clarku_youtube_crawler",
    version="2.0.6",
    author="Shuo Niu",
    author_email="ShNiu@clarku.edu",
    description="Clark University, Package for YouTube crawler and cleaning data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ClarkUniversity-NiuLab/clarku-youtube-crawler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    dependency_links=['https://pypi.org/project/google-api-python-client/'],
    install_requires=[
        'configparser',
        'datetime',
        'pytz',
        'pandas',
        'isodate',
        'xlrd',
        'youtube_transcript_api',
        'google-api-python-client'
    ],
    include_package_data=True,
    package_data={"clarku_youtube_crawler": ["US_CATE.json"]},
    python_requires='>=3.6',
)
