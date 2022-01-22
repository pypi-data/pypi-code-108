import setuptools



setuptools.setup(
    name='gbak',
    version='2.49',
    scripts=['gbak'],
    author="Thanh Hoa",
    author_email="getmoneykhmt3@gmail.com",
    description="A Des of gbak",
    long_description="Gbak",
    long_description_content_type="text/markdown",
    url="https://github.com/vtandroid/gbackup",
    packages=setuptools.find_packages(),
    py_modules=['gbackup','crypto'],
    install_requires=[
       'youtube-dl', 'google-api-python-client==1.7.11', 'click', 'google-auth-httplib2>=0.0.3','google-auth-oauthlib>=0.4.1','httplib2==0.15.0','cryptography'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )