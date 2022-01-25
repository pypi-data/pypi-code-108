import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unihiker",
    version="0.0.9",
    author="Angelo Qiao",
    author_email="angelo.qiao@dfrobot.com",
    description="Library for Unihiker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://wiki.unihiker.com",
    project_urls={
        "Bug Tracker": "https://mc.dfrobot.com.cn/forum-221-1.html",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    include_package_data=True,
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={
        "": ["*.ttf"],
    },
    install_requires=['fontTools', 'pillow', 'qrcode'],
    python_requires=">=3.6",
)