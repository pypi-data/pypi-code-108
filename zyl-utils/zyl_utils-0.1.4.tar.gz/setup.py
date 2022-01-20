from setuptools import setup, find_packages

setup(
    name='zyl_utils',
    version='0.1.4',
    description=(
        'optimizer'
    ),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='zyl',
    author_email='1137379695@qq.com',
    maintainer='zyl',
    maintainer_email='1137379695@qq.com',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/ZYuliang/zyl-utils',
    install_requires=[
        "tqdm",
        "transformers",
        "torch",
        "wandb",
        "loguru",
        "langid",
        "matplotlib",
        "numpy",
        "pandas",
        "typing",
        "simpletransformers",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
