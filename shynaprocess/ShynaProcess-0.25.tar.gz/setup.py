from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup_args = dict(
     name='ShynaProcess',
     version='0.25',
     packages=find_packages(),
     author="Shivam Sharma",
     author_email="shivamsharma1913@gmail.com",
     description="Shyna Backend Functionality Package For phase one processing",
     long_description=long_description,
     long_description_content_type="text/markdown",
    )

install_requires = [
    "setuptools",
    "wheel",
    'requests',
    'nltk',
    'feedparser',
    'ShynaTime',
    'google_speech',
    'ShynaDatabase',
    'googlesearch-python',
    'wikipedia',
    'sox'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
