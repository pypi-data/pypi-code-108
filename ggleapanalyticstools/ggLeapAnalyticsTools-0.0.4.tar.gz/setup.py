import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "ggLeapAnalyticsTools",
    version = "0.0.4",
    author = "Joshua \"Phosphorescent\" Mankelow",
    description = "A python package for helping users to generate and interact with data from ggLeap esports venue management software.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Phosphorescentt/ggLeapAnalyticsTools",
    project_urls = {
        "Bug Tracker": "https://github.com/Phosphorescentt/ggLeapAnalyticsTools/issues",
        },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        ],
    package_dir = {"": "src"}, 
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6",
)
