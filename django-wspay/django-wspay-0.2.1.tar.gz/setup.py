from setuptools import find_packages, setup


NAME = "django-wspay"
DESCRIPTION = "a payments Django app for WSPay"
AUTHOR = "Vedran Vojvoda"
AUTHOR_EMAIL = "vedran@pinkdroids.com"
URL = "https://github.com/pinkdroids/django-wspay"
LONG_DESCRIPTION = """
============
Django WSPay
============

This django app provides simple support for payments using WSPay gateway.
"""

tests_require = [
    "mock",
    "pytest",
    "pytest-django",
]

setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    version="0.2.1",
    license="MIT",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
    ],
    include_package_data=True,
    install_requires=[
        "django-appconf>=1.0.4",
        "django>=3.0",
        "pytz",
        "responses>=0.10.16",
    ],
    extras_require={
        "testing": tests_require,
    },
    zip_safe=False,
)
