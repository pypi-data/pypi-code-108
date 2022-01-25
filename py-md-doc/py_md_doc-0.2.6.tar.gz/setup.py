from setuptools import setup
from pathlib import Path

setup(
    name="py_md_doc",
    packages={"py_md_doc"},
    version="0.2.6",
    license="MIT",
    description="Generate markdown documentation for your Python scripts."
                "Like Sphinx, but simpler and directly compatible with GitHub.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Seth Alter",
    author_email="subalterngames@gmail.com",
    url="https://github.com/subalterngames/py_md_doc",
    download_url="https://github.com/subalterngames/py_md_doc/archive/0.1.tar.gz",
    keywords=["documentation", "doc", "sphinx", "markdown", "github"],
    install_requires=[""],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)
