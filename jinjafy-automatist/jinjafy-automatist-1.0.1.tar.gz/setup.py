import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jinjafy-automatist",
    version="1.0.1",
    author="Michael Murtaugh",
    author_email="mm@automatist.org",
    description="Tiny CLI wrapper for jinja2 templates",
    entry_points={
        'console_scripts': [
            'jinjafy=jinjafy:main',
        ],
    },
    install_requires=['setuptools', 'jinja2'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/activearchives/jinjafy",
    project_urls={
        "Bug Tracker": "https://gitlab.com/activearchives/jinjafy/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)