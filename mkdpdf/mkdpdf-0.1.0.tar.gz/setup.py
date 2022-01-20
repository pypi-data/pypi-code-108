import os

from setuptools import setup, find_packages

# package names for import tests
import_pkg_test = [
]

setup(
    name="mkdpdf",
    description="Python package render engine for Markdown (Markdown) and PDF (Weasyprint).",
    long_description=open(os.path.join(os.getcwd(), "README.md")).read().strip(),
    version=open(os.path.join(os.getcwd(), "VERSION")).read().strip(),
    url="https://gitlab.com/lgensinger/mkdpdf",
    install_requires=[d.strip() for d in open(os.path.join(os.getcwd(), "requirements.txt")).readlines()],
    extras_require={
        "test": [d.strip() for d in open(os.path.join(os.getcwd(), "requirements-test.txt")).readlines()] if os.path.exists(os.path.join(os.getcwd(), "requirements-test.txt")) else list()
    },
    import_pkg_test=import_pkg_test,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "generate-pdf=mdpdf.bin.generate_pdf:main"
        ],
    }
)
