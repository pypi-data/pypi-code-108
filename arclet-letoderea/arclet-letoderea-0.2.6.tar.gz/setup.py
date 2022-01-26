import setuptools

with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="arclet-letoderea",
    version="0.2.6",
    author="ArcletProject",
    author_email="rf_tar_railt@qq.com",
    description="A high-performance, simple-structured event system, relies on asyncio",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/rst",
    url="https://github.com/ArcletProject/Letoderea",
    packages=['arclet.letoderea', 'arclet.letoderea.entities',  'arclet.letoderea.breakpoint'],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords='asyncio, dict',
    python_requires='>=3.8'
)
