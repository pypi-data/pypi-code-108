
from setuptools import find_packages
from setuptools import setup
import platform
import os

package_data = []
for d, ds, fs in os.walk("trtpy/include"):
    d = d.replace("trtpy/", "")
    package_data.extend([os.path.join(d, file) for file in fs])

# for d, ds, fs in os.walk("trtpy/lib"):
#     d = d.replace("trtpy/", "")
#     package_data.extend([os.path.join(d, file) for file in fs])

#package_data.append("script/trtpy")

setup(
    name="trtpy-dev",
    version="1.1.0",
    author="djw.hope",
    author_email="512690069@qq.com",
    url="https://github.com/shouxieai/tensorRT_cpp",
    description="TensorRTPro python interface",
    python_requires=">=3.7",
    install_requires=["numpy", "requests", "tqdm"],
    packages=find_packages(),
    package_data={
        "": package_data
    },
    zip_safe=False,
    platforms="linux"
)
