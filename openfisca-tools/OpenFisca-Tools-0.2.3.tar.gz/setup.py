from setuptools import setup, find_packages

setup(
    name="OpenFisca-Tools",
    version="0.2.3",
    author="PolicyEngine",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url="https://github.com/policyengine/openfisca-tools",
    install_requires=[
        "OpenFisca-Core",
        "microdf_python",
        "numpy",
        "pandas",
        "wheel",
    ],
    packages=find_packages(),
)
