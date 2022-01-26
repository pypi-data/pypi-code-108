import setuptools

with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="arclet-edoves",
    version="0.0.10",
    author="ArcletProject",
    author_email="rf_tar_railt@qq.com",
    description="A new abstract framework based on Cesloi ",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/rst",
    url="https://github.com/ArcletProject/Edoves",
    install_requires=['aiohttp', 'yarl', 'pydantic', 'loguru', 'arclet-letoderea', 'arclet-alconna'],
    packages=['arclet.edoves', 'arclet.edoves.builtin',  'arclet.edoves.main', 'arclet.edoves.message', 'arclet.edoves.utilles', 'arclet.edoves.builtin.event', 'arclet.edoves.builtin.mah', 'arclet.edoves.builtin.mah.module'],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords='mirai, bot, asyncio, http, websocket',
    python_requires='>=3.8'
)
