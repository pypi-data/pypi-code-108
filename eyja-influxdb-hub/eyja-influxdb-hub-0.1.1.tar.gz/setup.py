from setuptools import find_packages, setup


setup(
    name='eyja-influxdb-hub',
    zip_safe=True,
    version='0.1.1',
    description='InfluxDB Plugin for Eyja',
    url='https://gitlab.com/public.eyja.dev/eyja-influxdb-hub',
    maintainer='Anton Berdnikov',
    maintainer_email='agratoth@yandex.ru',
    packages=find_packages(),
    package_dir={'eyja_influxdb': 'eyja_influxdb'},
    install_requires=[
        'eyja-internal>=0.4.1',
        'influxdb>=5.3.1',
        'influxdb-client>=1.25.0',
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
