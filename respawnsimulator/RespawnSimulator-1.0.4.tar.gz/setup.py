import setuptools

try:
    with open('README.md', encoding="utf-8") as f:
        long_description = f.read()
except Exception as e:
    long_description = "Long Description Load Failed"
    print(str(e))
    exit(0)
setuptools.setup(
    name="RespawnSimulator",
    version="1.0.4",
    author="N0P3",
    author_email="n0p3@qq.com",
    description="A respawn simulator framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    py_modules=["property", "event", "character", "utils"]
)
