import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

project_urls = {
    'Documentation': 'https://htmlpreview.github.io/?https://bitbucket.org/kds_consulting_team/python-csv-writer/raw'
                     '/92caae145a6eb38f0615c98620803505aee4ec88/docs/api-html/keboola/csvwriter/core.html'
}

setuptools.setup(
    name="keboola.csvwriter",
    version="1.0.1",
    author="Keboola Component Factory Team",
    project_urls=project_urls,
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    author_email="support@keboola.com",
    description=" ElasticDictWriter module based on Python csv package ensuring consistent header in the final CSV.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/kds_consulting_team/python-csv-writer/src/master/",
    packages=['keboola.csvwriter'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.7'
)
