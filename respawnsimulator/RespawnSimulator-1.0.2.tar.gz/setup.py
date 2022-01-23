import setuptools

setuptools.setup(
    name="RespawnSimulator",
    version="1.0.2",
    author="N0P3",
    author_email="n0p3@qq.com",
    description="A respawn simulator framework",
    packages=setuptools.find_packages(),
    py_modules=["__init__", "property", "event", "character", "utils"]
)

