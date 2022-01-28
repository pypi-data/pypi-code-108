#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("nebpyclient/VERSION", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="nebpyclient",
    version=version,
    author="Nebulon, Inc.",
    author_email="info@nebulon.com",
    description="The Nebulon Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nebulon/nebpyclient",
    packages=setuptools.find_packages(),
    package_data={
        "nebpyclient": ["VERSION"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests'
    ],
    python_requires=">=3.6",
)
