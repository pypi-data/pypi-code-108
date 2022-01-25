import os

import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

buildVersion = os.getenv('CI_PIPELINE_IID')
if buildVersion is None:
  buildVersion = "99"  # Fake local dev version

refName = os.getenv('CI_COMMIT_REF_NAME')
if refName is not None and len(refName) > 0 and refName[0] == 'v':
  majorMinorVersion = refName[1:]
else:
  majorMinorVersion = '0.0'

setuptools.setup(
    name="kubedev",
    version=f"{majorMinorVersion}.{buildVersion}",
    author="Daniel Albuschat",
    author_email="d.albuschat@gmail.com",
    description="Kubernetes development workflow made easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/daniel.albuschat.gira/kubedev",
    packages=['kubedev', 'kubedev.utils'],
    package_data={'kubedev': ['templates/*']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['kubedev=kubedev:main'],
    },
    install_requires=[
        'pyyaml',
        'ruamel-yaml',
        'colorama'
    ]
)
