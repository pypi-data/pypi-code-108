import os

from setuptools import find_namespace_packages, setup

__name__ = 'vatis_asr_amqp'
__tag__ = '1.0.1'
__short_description__ = 'AMQP client implementation over Pika library'
__download_url__ = 'https://gitlab.com/vatistech/asr-amqp/-/archive/{__tag__}/asr_amqp-{__tag__}.zip'\
    .format(__tag__=__tag__)

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
__release_status__ = "Development Status :: 4 - Beta"


def req_file(filename, folder="requirements"):
    with open(os.path.join(folder, filename)) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters
    # Example: `\n` at the end of each line
    return [x.strip() for x in content]


install_requires = req_file('requirements.txt')

packages = find_namespace_packages(include=['vatis.*'])

namespaces = ['vatis']

setup(
    name=__name__,
    version=__tag__,
    description=__short_description__,
    url='https://gitlab.com/vatistech/asr-amqp',
    download_url=__download_url__,
    maintainer='VATIS TECH',
    maintainer_email='support@vatis.tech',
    packages=packages,
    namespace_packages=namespaces,
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    python_requires=">=3.6",
    classifiers=[
            __release_status__,
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Build Tools",
            "Topic :: Internet"
    ]
)
