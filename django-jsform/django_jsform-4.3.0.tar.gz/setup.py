import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('VERSION', 'r') as fh:
    version = fh.read()

setuptools.setup(
    name="django_jsform",
    version=version,
    author="Alex Fischer",
    author_email="alex@quadrant.net",
    description="Django integration for jsform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quadrant-newmedia/django_jsform",
    packages=['django_jsform'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["Django>=2.2,<3.3"],
    include_package_data=True,
)