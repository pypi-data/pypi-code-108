import setuptools
with open("README.md", "r",encoding='utf-8') as fh:
  long_description = fh.read()


setuptools.setup(
  name="flask-simpleserialize",
  version="0.0.3",
  author="张斌",
  author_email="786017877@163.com",
  description="一个针对于flask框架的序列化工具",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/pypa/sampleproject",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)
