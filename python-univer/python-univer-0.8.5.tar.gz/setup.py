import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-univer",
    version="0.8.5",
    author="Nauryzbek Aitbayev",
    author_email="nauryzbek.aitbayev@yu.edu.kz",
    description="Данная библиотека содержить SqlAlchemy ORM для системы Univer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yessenovuniversity/python_univer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'sqlalchemy',
        'pyodbc',
    ],
    python_requires='>=3.6',
)
