import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="nonebot-plugin-gamedraw",
  version="0.2.1",
  author="HibiKier",
  author_email="775757368@qq.com",
  description="Nonebot2插件",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/HibiKier/nonebot_plugin_gamedraw",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
)
