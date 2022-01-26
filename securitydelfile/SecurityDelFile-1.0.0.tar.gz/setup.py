from setuptools import setup
setup(
    name="SecurityDelFile",
    version="1.0.0",
    packages=["SecurityDelFile"],
    description="SecurityDelFile",
    author="liuzihao",
    keywords="Security Del File app",
    install_requires=[],
    python_requires=">=3",
    entry_points={
        'console_scripts': [
            'SecurityDelFile=SecurityDelFile:runapp',
            'sdf=SecurityDelFile:runapp',
            'SDF=SecurityDelFile:runapp',
        ]
    },
    # project_urls={
    #     "Source Code":"https://gitee.com/haozihan/msgs/tree/master/",
    # },
)
