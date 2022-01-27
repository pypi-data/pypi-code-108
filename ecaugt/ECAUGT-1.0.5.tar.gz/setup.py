import setuptools

with open("ECAUGTdoc_v0721.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ECAUGT",
    version="1.0.5",
    author="Yixin Chen & Haiyang Bian",
    author_email="chenyx19@mails.tsinghua.edu.cn",
    maintainer='Minsheng Hao',
    maintainer_email="hmsh653@gmail.com",
    description="ECA Client",
    packages=setuptools.find_packages(),
    package_data={
        # 引入任何包下面的 *.txt、*.rst 文件
        "": ["*.csv"],
    },
    install_requires=[
        'tablestore>=5.2.1',
        'numpy',
        'pandas'
        ],
    liciense='GPL',
    keywords=["Client", "ECA"],
    python_requires='>=3',
    long_description_content_type='text/markdown',
    long_description=long_description
)
