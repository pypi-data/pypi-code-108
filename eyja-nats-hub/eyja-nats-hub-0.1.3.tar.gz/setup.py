from setuptools import find_packages, setup


setup(
    name='eyja-nats-hub',
    zip_safe=True,
    version='0.1.3',
    description='Eyja Hub for NATS',
    url='https://gitlab.com/public.eyja.dev/eyja-nats-hub',
    maintainer='Anton Berdnikov',
    maintainer_email='agratoth@yandex.ru',
    packages=find_packages(),
    package_dir={'eyja_nats': 'eyja_nats'},
    install_requires=[
        'eyja-internal>==0.3.24',
        'nats-py==2.0.0rc5',
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
