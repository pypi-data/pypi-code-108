from setuptools import setup, find_packages


with open("README.md", "r") as readme_file:
    readme_text = readme_file.read()


setup_args = dict(
    name='simplestr',
    version='0.5.0',
    description="Simple annotations to automatically generate __str__(self), __repr__(self) and __eq__(self, other) methods in classes",
    keywords=['str', 'repr', 'eq', 'generate', 'automatic', 'annotation'],
    long_description=readme_text,
    long_description_content_type="text/markdown",
    license='Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License',
    packages=find_packages(),
    author="Leo Ertuna",
    author_email="leo.ertuna@gmail.com",
    url="https://github.com/jpleorx/simplestr",
    download_url='https://pypi.org/project/simplestr/'
)


install_requires = []


if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
