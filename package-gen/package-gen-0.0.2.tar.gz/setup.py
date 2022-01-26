import setuptools

setuptools.setup(
    name="package-gen",
    version="0.0.2",
    author="Zhang",
    author_email="",
    url = 'https://github.com/suifengpiaoyang/pk-gen',
    description="Generate python package",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pk-gen=packagegenerator:main",
        ]
    },
    python_requires='>=3.6.0'
)