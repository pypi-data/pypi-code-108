import setuptools


with open('README.md', 'r', encoding='utf-8') as fl:
    long_description = fl.read()


setuptools.setup(
    name="package-gen",
    version="0.0.5",
    author="Zhang",
    author_email="",
    url='https://github.com/suifengpiaoyang/package-gen',
    description="Generate python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pk-gen=packagegenerator:main",
        ]
    },
    python_requires='>=3.6.0'
)
