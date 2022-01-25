import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyTransit-CTA',
    version='1.0.0',
    author='Joe Rechenmacher',
    author_email='joe.rechenmacher@gmail.com',
    description='Python CTA Transit Feed Wrapper',
    url='https://github.com/joerex1418/cta',
    project_urls = {
        "Issues": "https://github.com/joerex1418/cta/issues",
        "Projects": "https://github.com/joerex1418/cta/projects"
    },
    license='GPU',
    packages=setuptools.find_packages(where='cta',include=["__init__"],exclude=["cta","constants","utils","utils_cta"]),
    install_requires=['requests','pandas','beautifulsoup4','polars'],
)
