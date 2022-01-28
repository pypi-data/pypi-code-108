import setuptools
from version import get_git_version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
	name='score_ecard',
	version=get_git_version(),
	description='random forest + lr card',
	url='https://github.com/wqwangchn/score_ecard',
	author='wqwangchn',
	author_email='wqwangchn@163.com',
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=setuptools.find_packages(),
	include_package_data=True,
	install_requires=['pandas','numpy','scipy','interval'],
	classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	],
	zip_safe=False
)
