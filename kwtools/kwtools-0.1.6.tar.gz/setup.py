"""
Setup for the kwtools package.

"""

import setuptools


# [Notes]: Do not add standard library
install_requires = [
    # requests
    "retry", "pysnooper", "user_agent", "requests",
    "uuid", "exchangelib", "urllib3", "schedule",
    "websocket", "PyExecJS", "aiohttp",

    # data process
    "numpy", "pandas", "xlsxwriter",

    # database
    "pymongo", "redis",
    "pymysql", "sqlalchemy",

    # encrypt
    "pycryptodome",
]

def get_package_info():
    import kwtools
    version = kwtools.__version__
    package_name = kwtools.__name__
    description = kwtools.__description__
    author = kwtools.__author__
    author_email = kwtools.__author_email__
    package_info = {
        "package_name":package_name, "version":version, "description":description,
        "author":author, "author_email":author_email,
    }
    return package_info

def get_readme():
    with open('README.md') as f:
        README = f.read()
    return README


if __name__ == "__main__":
    package_info = get_package_info()
    setuptools.setup(
        name=package_info["package_name"],
        version=package_info["version"],
        description=package_info["description"],
        long_description=get_readme(),
        author=package_info["author"],
        author_email=package_info["author_email"],
        license="MIT",
        url='https://github.com/kerwin6182828/kwtools',
        packages=setuptools.find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*", "*.tags*"]),
        python_requires=">=3.6",
        include_package_data=True,  #
        install_requires=install_requires,
        classifiers=[
            # Trove classifiers
            # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Intended Audience :: Developers',
        ],
    )
