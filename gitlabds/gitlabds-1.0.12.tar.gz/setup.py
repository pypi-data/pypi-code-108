import setuptools, os
from pathlib import Path

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
elif os.environ.get('CI_JOB_ID'):
    version = os.environ['CI_JOB_ID']

requires = ["pandas>=1.0.1", "numpy>=1.19.1", "scipy>=1.5.4", "scikit-learn>=0.23.1", "imbalanced-learn>=0.8.0"]

# read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name='gitlabds',
    version=version,
    description='Gitlab Data Science and Modeling Tools',
    long_description = long_description,
    long_description_content_type ='text/markdown',
    author='Kevin Dietz',
    author_email='kdietz@gitlab.com',
    packages=setuptools.find_packages(),
    url='https://gitlab.com/gitlab-data/gitlabds',
    python_requires= '>=3.6',
    install_requires=requires,
)  

