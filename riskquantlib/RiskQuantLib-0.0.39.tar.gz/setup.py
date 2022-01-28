#!/usr/bin/python
#coding = utf-8

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RiskQuantLib", # Replace with your own username
    version="0.0.39",
    author="Syuya_Murakami",
    author_email="wxy135@mail.ustc.edu.cn",
    description="RiskQuantLib is a QuantLib derivative to evaluate risk.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://riskquantlib-doc.readthedocs.io/en/latest/index.html",
    project_urls={
        "Bug Tracker": "https://github.com/SyuyaMurakami/RiskQuantLib",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'newRQL = RiskQuantLib:newProject',
            'saveRQL = RiskQuantLib:saveProject',
            'tplRQL = RiskQuantLib:unpackProject',
            'pkgRQL = RiskQuantLib:packProject',
            'addRQL = RiskQuantLib:addProjectTemplate',
            'delRQL = RiskQuantLib:delProjectTemplate',
            'clearRQL = RiskQuantLib:clearAllProjectTemplate',
            'listRQL = RiskQuantLib:listProjectTemplate'
        ]
    }
)
