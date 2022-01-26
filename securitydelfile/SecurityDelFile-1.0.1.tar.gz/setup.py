from setuptools import setup
setup(
    name="SecurityDelFile",
    version="1.0.1",
    packages=["SecurityDelFile"],
    description="SecurityDelFile",
    author="liuzihao",
    keywords="Security Del File app",
    install_requires=[],
    python_requires=">=3",
    entry_points={
        'console_scripts': [
            'SecurityDelFile=SecurityDelFile:run',
            'sdf=SecurityDelFile:run',
            'SDF=SecurityDelFile:run',
        ]
    },
    # project_urls={
    #     "Source Code":"https://gitee.com/haozihan/",
    # },
)
