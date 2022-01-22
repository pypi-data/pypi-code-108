from setuptools import setup, find_packages


setup(
    name="proxy-class",
    version="0.0.1",
    description="Proxy class",
    long_description_content_type="text/markdown",
    author='Tomasz Król',
    author_email='tomasz.kingu.krol@gmail.com',
    maintainer='Tomasz Król',
    maintainer_email='tomasz.kingu.krol@gmail.com',
    url='https://github.com/tomaszkingukrol/proxy-class',
    project_urls={
        "Bug Tracker": "https://github.com/tomaszkingukrol/proxy-class/issues",
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
)