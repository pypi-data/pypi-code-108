from setuptools import setup, find_packages

setup(
    name="calculator_teh",
    version="1.0.0",
    description="Simple calc functions",
    author="Het Shah",
    author_email="hetshah2000@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={"console_scripts": ["packaging=calculator_functions.calculate:main"]},
)
