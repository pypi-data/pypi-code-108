# _*_coding     : UTF_8_*_
# Author        :Jie Shen
# CreatTime     :2022/1/25 10:59

import setuptools
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name='jshen',  # How you named your package folder (foo)
    # packages=['jshen'],  # Chose the same as "name"
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    platforms="any",
    version='0.0.2',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Tools for leetcode,kaggle...',  # Give a short description about your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='J.Shen',  # Type in your name
    author_email='shenjiecn@qq.com',  # Type in your E-Mail
    url='https://github.com/JieShenAI/jshen/',  # Provide either the link to your github or to your website
    # download_url = 'https://github.com/JieShenAI/jshen/Cookie2Dict/archive/master.zip',
    keywords=['TreeNode'],  # Keywords that define your package best
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
