from setuptools import setup, find_packages

VERSION = '0.0.3' 
DESCRIPTION = 'My first Python package'
LONG_DESCRIPTION = 'My first Python package with a slightly longer description'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="algotradingPythonSalem", 
        url="https://initialcommit.com/projects/algotradingPythonSalem.com",
        version=VERSION,
        author="Jason Dsouza",
        author_email="AlgoTrading@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)



# import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

# setuptools.setup(
#     name="algotradingPythonSalem",
#     version="0.0.2",
#     author="AlgoTrading",
#     author_email="AlgoTrading@gmail.com",
#     description="Find and tag Git commits based on version numbers in commit messages.",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://initialcommit.com/projects/algotradingPythonSalem.com",
#     packages=setuptools.find_packages(),
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#     ],
#     python_requires='>=3.6',
#     install_requires=[
#         'gitpython'
#     ],
#     keywords='git tag git-tagup tagup tag-up version autotag auto-tag commit message',
#     project_urls={
#         'Homepage': 'https://initialcommit.com/projects/algotradingPythonSalem.com',
#     },
#     entry_points={
#         'console_scripts': [
#             'git-tagup=main:app',
#             'gtu=src.main:app',
#         ],
#     },
# )