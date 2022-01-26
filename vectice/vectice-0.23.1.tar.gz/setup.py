import sys
import os
from setuptools import setup

if sys.version_info < (3, 7):
    print("vectice requires Python 3 version >= 3.7.", file=sys.stderr)
    sys.exit(1)

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.rst")

version_requires = ">=3.7.1"

with open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()
    readme.replace("Python >= 3.7.1", f"Python {version_requires}")


setup(
    name="vectice",
    version="0.23.1",
    description="Vectice Python library",
    long_description=readme,
    author="Vectice Inc.",
    author_email="sdk@vectice.com",
    url="https://github.com/vectice/vectice-python",
    packages=[
        "vectice",
        "vectice.api",
        "vectice.api.output",
        "vectice.adapter",
        "vectice.entity",
        "vectice.models",
        "vectice.utils",
    ],
    license="Apache License 2.0",
    keywords=["Vectice", "Client", "API", "Adapter"],
    platforms=["Linux", "MacOS X", "Windows"],
    python_requires=version_requires,
    install_requires=[
        "requests >= 2.5.0",
        "urllib3",
        "python-dotenv >= 0.10.0",
    ],
    tests_require=["mock >= 1.0.1", "pytest", "coverage", "pytest-cov", "testcontainers"],
    extras_require={
        "dev": ["bandit", "black", "flake8", "mypy", "pre-commit", "Pygments"],
        "mlflow": ["mlflow"],
        "doc": ["sphinx", "recommonmark", "nbsphinx", "sphinx-rtd-theme", "pypandoc", "jupyterlab"],
        "git": ["GitPython"],
        "github": ["PyGithub"],
        "bitbucket": ["atlassian-python-api"],
        "gitlab": ["python-gitlab"],
        "pandas": ["pandas"],
        "jupyter": ["jupyter_core", "ipykernel", "traitlets"],
        "collab": ["oauth2client", "GitPython >= 3.1.14"],
        "bigquery": ["google-cloud-bigquery >= 2.32.0", "google-cloud-bigquery-storage >= 2.11.0"],
        "gcs": ["google-cloud-storage"],
    },
    classifiers=[
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
)
