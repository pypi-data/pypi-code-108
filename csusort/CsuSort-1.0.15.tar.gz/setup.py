from setuptools import setup, find_packages  # 这个包没有的可以pip一下

setup(
    name="CsuSort",  # 这里是pip项目发布的名称
    version="1.0.15",  # 版本号，数值大的会优先被pip
    keywords=["pip", "sort"],
    description="person or car",
    license="MIT Licence",
    author="csu_ywj",
    packages=find_packages(),
    data_files=[],
    include_package_data=True,
    platforms="any",
    install_requires=["Keras>=2.3.1", "tensorflow-gpu>=1.15.2", "numpy>=1.16.0", "opencv-python>=3.4.4.19", "scikit-learn>=0.21.2",
                      "scipy>=1.1.0", "Pillow", "torch>=1.3.0", "torchvision>=0.4.1"]
)