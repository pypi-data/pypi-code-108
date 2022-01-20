import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="wagtailcloudinary",
    version="1.2.0",
    packages=find_packages(include=["wagtailcloudinary"], exclude=["sandbox"]),
    install_requires=["cloudinary", "wagtail"],
    include_package_data=True,
    license="BSD Licence",
    description="Cloudinary support for Wagtail CMS",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/thelabnyc/wagtailcloudinary",
    author="Davor Teskera",
    author_email="dteskera@gmail.com",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.1",
        "Framework :: Wagtail",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
