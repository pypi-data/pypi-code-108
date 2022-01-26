import setuptools, os

setuptools.setup(
    name="example-pkg-naturalett",  # Replace with your own PyPi
    version=os.environ.get("BUILD_VERSION", "14.8"),
    author="Foo Bar",
    author_email="lidor.ettinger@example.com",
    description="A small example package",
    url="https://github.com/naturalett/getting-started",
    install_requires=['distribution-Final', 'boto3'],
    packages=['calculate'],
    scripts=['calculate/calc.py'],
    python_requires='>=3.9',
)
