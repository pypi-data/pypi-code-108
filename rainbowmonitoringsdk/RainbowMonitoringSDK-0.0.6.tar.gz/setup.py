import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

reqs = ['requests', 'pyyaml', 'Flask', 'kafka', 'ConfigUpdater', 'docker']

setuptools.setup(
    name="RainbowMonitoringSDK",
    version="0.0.6",
    author="Moysis Symeonides, Joanna Georgiou",
    author_email="symeonidis.moysis@cs.ucy.ac.cy, georgiou.joanna@cs.ucy.ac.cy",
    description="The Rainbow's Monitoring SDK library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="code"),
    package_dir={'': 'code'},
    python_requires='>=3.5',
    install_requires=reqs
)
