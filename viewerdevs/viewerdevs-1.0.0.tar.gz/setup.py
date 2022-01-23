from setuptools import setup, find_packages


setup(
    name='viewerdevs',
    version='1.0.0',
    description="Doujin/Image Viewer for nhentaidevs.",
    author="John Lester Dev :>",
    author_email="johnlesterincbusiness@gmail.com",
    url="https://pypi.org/project/viewerdevs",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "nhentaidevs",
        "pillow",
        "click",
        "tqdm",
    ],
    keywords=[
        "nhentaidevs",
        "tkinter",
        "window"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
