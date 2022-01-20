import setuptools

setuptools.setup(
    name="params-guidline",
    version="0.0.3",
    license='MIT',
    author="wo7864",
    author_email="wo78644@gmail.com",
    description="params-guidline",
    long_description=open('README.md').read(),
    url="https://github.com/wo7864/params_guideline",
    packages=setuptools.find_packages(),
    py_modules=['pg'],
    classifiers=[
        # 패키지에 대한 태그
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)