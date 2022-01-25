from setuptools import find_packages, setup


setup(
    name='eyja-internal',
    zip_safe=True,
    version='0.4.0',
    description='Smart async framework',
    url='https://gitlab.com/public.eyja.dev/eyja-internal',
    maintainer='Anton Berdnikov',
    maintainer_email='agratoth@yandex.ru',
    packages=find_packages(),
    package_dir={'eyja': 'eyja'},
    install_requires=[
        'aiofiles>=0.8.0',
        'pydantic>=1.8.2',
        'pytz>=2021.3',
        'PyYAML>=6.0',
        'jinja2>=3.0.3',
        'uvloop>=0.16.0',
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.8',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
