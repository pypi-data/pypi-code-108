from setuptools import setup

with open('README.md') as f:
    readme = f.read()


# This call to setup() does all the work
setup(
    name="kcapi",
    version="1.0.6",
    description="A module to automate stuff in Keycloak.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/cesarvr/keycloak-api",
    author="cesar valdez",
    author_email="cesar.valdez@gosub.biz",
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
    packages=["kcapi", "kcapi.rest", "kcapi.ie"],
    include_package_data=False,
    install_requires=["requests"],
)
