import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eisenradio", # project name /folder
    version="0.0.1",
    author="René Horn",
    author_email="rene_horn@gmx.net",
    description="Play radio. Record radio. Style your App.",
    long_description=long_description,
    license='gpl-3.0',
    long_description_content_type="text/markdown",
    url="",
    include_package_data=True,
    packages=setuptools.find_packages(),
        install_requires=[
		'flask_cors',
        'configparser',
        'requests',
        'urllib3'
    ],
    classifiers=[
    # How mature is this project? Common values are
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
    ],
    python_requires='>=3.6',
)
# https://stackoverflow.com/questions/20288711/post-install-script-with-python-setuptools
# from setuptools import setup
def _post_install():
    print('----------------------------- POST INSTALL ----------------------------------')
    # setup(...)
    post_install()