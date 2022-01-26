from setuptools import setup

from ssl_metrics_git_productivity import version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ssl-metrics-git-productivity",
    packages=["ssl_metrics_git_productivity"],
    version=version.version(),
    description="SSL Metrics - Git Productivity",
    author="Software and Systems Laboratory - Loyola University Chicago",
    author_email="ssl-metrics@ssl.luc.edu",
    license="BSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ssl.cs.luc.edu/projects/metricsDashboard",
    project_urls={
        "Bug Tracker": "https://github.com/SoftwareSystemsLaboratory/ssl-metrics-git-productivity/issues",
        "GitHub Repository": "https://github.com/SoftwareSystemsLaboratory/ssl-metrics-git-productivity",
    },
    keywords=[
        "bus factor",
        "commits",
        "engineering",
        "git",
        "github",
        "issue density",
        "issues",
        "kloc",
        "loyola",
        "loyola university chicago",
        "luc",
        "mining",
        "metrics",
        "repository",
        "repository mining",
        "simple",
        "software",
        "software engineering",
        "software metrics",
        "software systems laboratory",
        "ssl"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.9",
    install_requires=[
        "matplotlib>=3.4.3",
        "numpy>=1.21.2",
        "pandas>=1.3.3",
        "scikit-learn>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "ssl-metrics-git-productivity-compute = ssl_metrics_git_productivity.main:main",
            "ssl-metrics-git-productivity-graph = ssl_metrics_git_productivity.create_graph:main",
        ]
    },
)
