import setuptools

setuptools.setup(
    name='coolbg',
    version='3.92',
    author="Thanh Hoa",
    author_email="thanhhoakhmt1@gmail.com",
    description="A Des of coolbg",
    long_description="Des",
    long_description_content_type="text/markdown",
    url="https://github.com/vtandroid/dokr",
    packages=setuptools.find_packages(),
    py_modules=['bgeditor'],
    install_requires=[
        'requests', 'numpy', 'moviepy','Pillow', 'youtube_dl','gbak'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )