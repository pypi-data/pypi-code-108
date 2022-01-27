from setuptools import find_packages, setup
import yamhl

setup(
    name="yamhl",
    author="whinee",
    author_email="whinyaan@gmail.com",
    version=yamhl.__version__,
    description="Yet Another Markdown 2 HTML Library",
    url="https://yamhl.pages.dev",
    project_urls={
        'Documentation': 'https://yamhl.pages.dev/docs',
        'Source': "https://github.com/Pirate-Kings/yamhl",
        'Tracker': 'https://github.com/Pirate-Kings/yamhl/issues',
    },
    license="MIT",
    keywords='',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "httpx",
        "mako",
        "pdoc3",
        "pyyaml",
    ],
)
