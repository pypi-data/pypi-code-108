import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="allocation_language",
    version="0.0.1",
    description="Language intented to construct the financial behaviour of (re)insurance contracts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "rply"
    ],
    author="Mammen Joseph",
    author_email="tmammenjoseph@gmail.com",
    maintainer="Mammen Joseph",
    maintainer_email="tmammenjoseph@gmail.com",
    url="",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
