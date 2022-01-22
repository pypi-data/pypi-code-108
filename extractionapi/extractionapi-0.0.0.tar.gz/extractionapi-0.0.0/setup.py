from setuptools import setup, find_packages

readme = ''
with open('README.md') as f:
    long_description = f.read()

setup(
    name="extractionapi",
    version="0.0.0",
    url="https://github.com/CNDRD/extraction-api",
    description="Rainbow Six Extraction API interface",
    author="CNDRD",
    packages=find_packages(),
    license="MIT",
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.8.0",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ]
)
