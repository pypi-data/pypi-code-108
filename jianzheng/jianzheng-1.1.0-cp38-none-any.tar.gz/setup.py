import setuptools

setuptools.setup(
    name="jianzheng",
    version="1.1.0",
    license='Apache 2.0',
    author="Jianzheng Luo",
    author_email="jianzheng.luo.china@gmail.com",
    url="https://github.com/JianzhengLuo/jianzheng",
    description="Some fast-to-use APIs those provide ML solutions.",
    long_description=(long_description := open(
        "./README.md", "r", encoding="utf-8")).read(),
    long_description_content_type="text/markdown",

    project_urls={
        "Bug Tracker": "https://github.com/JianzhengLuo/jianzheng/issues"
    },

    classifiers=[
        "Development Status :: 1 - Planning",

        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",

        "License :: OSI Approved :: Apache Software License",

        "Natural Language :: English",

        "Programming Language :: Python :: 3.8"
    ],
    python_requires=">=3.8",

    package_dir={"": "./src"},
    packages=setuptools.find_packages(where="./src")
)


long_description.close()
