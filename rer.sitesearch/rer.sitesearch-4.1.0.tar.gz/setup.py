from setuptools import setup, find_packages

version = "4.1.0"

setup(
    name="rer.sitesearch",
    version=version,
    description="A product that change the base site search of Plone with some new features.",
    long_description=open("README.rst").read() + "\n" + open("CHANGELOG.rst").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: Addon",
        "Framework :: Plone",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python",
    ],
    keywords="Python Plone Search",
    author="RedTurtle Technology",
    author_email="sviluppo@redturtle.it",
    url="https://github.com/RegioneER/rer.sitesearch",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/rer.sitesearch",
        "Source": "https://github.com/RegioneER/rer.sitesearch",
        "Tracker": "https://github.com/RegioneER/rer.sitesearch/issues",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["rer"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "plone.api>=1.8.4",
        "plone.restapi",
        "plone.app.dexterity",
        "collective.z3cform.jsonwidget",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            "collective.MockMailHost",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = rer.sitesearch.locales.update:update_locale
    """,
)
