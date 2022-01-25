import setuptools

import versioneer

documentation_requirements = [
    "Sphinx",
    "m2r2",
    "sphinx-autodoc-typehints",
    "sphinx-rtd-theme",
]

setuptools.setup(
    name="preheat_open",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Neogrid and contributors",
    author_email="analytics@neogrid.dk",
    description="Python wrapper for Neogrid Technologies' REST API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/neogrid-technologies-public/preheat-open-python",
    project_urls={
        "Bug Tracker": "https://gitlab.com/neogrid-technologies-public/preheat-open-python/-/issues",
        "Documentation": "https://neogrid-technologies-public.gitlab.io/preheat-open-python",
        "Source Code": "https://gitlab.com/neogrid-technologies-public/preheat-open-python",
    },
    packages=setuptools.find_packages(),
    install_requires=["dateutils", "requests", "pandas", "numpy", "networkx"],
    extras_require={
        "doc": documentation_requirements,
        "dev": [
            "setuptools>=42",
            "wheel",
            "pytest",
            "pytest-cov",
            "pytest-xdist",
        ]
        + documentation_requirements,
    },
)
