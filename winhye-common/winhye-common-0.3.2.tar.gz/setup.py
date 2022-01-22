import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="winhye-common",
    version="0.3.2",
    author="千城",
    author_email="qiancheng0402@163.com",
    description="public package including ES, logging, oss, db...",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://e.gitee.com/winhye998/repos/winhye998/winhye-common",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "flask",
        "requests",
        "paho-mqtt",
        "websocket-server",
        "sqlalchemy",
        "psycopg2",
        "oss2",
        "crypto",
        "gevent"
    ]
)
