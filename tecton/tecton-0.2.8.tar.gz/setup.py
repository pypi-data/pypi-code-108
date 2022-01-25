import setuptools
import os

with open('README.md') as readme_f:
  long_description = readme_f.read()

packages = setuptools.find_packages()
for root, _, files in os.walk("tecton_proto"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))
for root, _, files in os.walk("protoc_gen_swagger"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))

setuptools.setup(
    classifiers=['Programming Language :: Python :: 3', 'Operating System :: OS Independent', 'License :: Other/Proprietary License'],
    python_requires='>=3.7.*',
    author='Tecton, Inc.',
    author_email='support@tecton.ai',
    url='https://tecton.ai',
    license='Tecton Proprietary',
    include_package_data=True,
    description='Tecton Python SDK',
    entry_points={'console_scripts': ['tecton=tecton.cli.cli:main']},
    name='tecton',
    version='0.2.8',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['attrs==19.2.0', 'boto3', 'dill', 'googleapis-common-protos==1.52.0', 'grpcio', 'jinja2', '# 1.20 breaks older versions of pyarrow', '# https://stackoverflow.com/questions/67502942/arrowtypeerror-did-not-pass-numpy-dtype-object-conversion-failed-for-column', 'numpy>=1.16.5,<1.20', 'pathspec', 'pendulum==2.1.2', 'protobuf==3.13.0', 'pytimeparse', 'pandas>=0.25.0,<=1.1.5', 'texttable', 'requests', 'colorama==0.4.3', 'tqdm==4.41.1', 'yaspin==0.16.0', 'typing-extensions==3.7.4.1', '# 2.7.4 and greater fix the CVEs listed below:', '# * https://security.snyk.io/vuln/SNYK-PYTHON-PYGMENTS-1088505', '# * https://security.snyk.io/vuln/SNYK-PYTHON-PYGMENTS-1086606', 'pygments>=2.7.4', 'pytest==5.4.3', 'click==7.1.2', 'typeguard', 'sqlparse'],
    extras_require={'databricks-connect': ['databricks_connect~=6.4.28', 'pyarrow==0.13.0'], 'databricks-connect6': ['databricks_connect~=6.4.28', 'pyarrow==0.13.0'], 'databricks-connect7': ['databricks-connect~=7.3.22', 'pyarrow==0.15.1'], 'databricks-connect9': ['databricks-connect~=9.1.0', 'pyarrow==5.0.0'], 'pyspark': ['pyspark==3.1.2', 'pyarrow==5.0.0'], 'pyspark2': ['pyspark==2.4.4', 'pyarrow==0.13.0'], 'pyspark3': ['pyspark==3.1.2', 'pyarrow==5.0.0'], 'pyspark3.1': ['pyspark==3.1.2', 'pyarrow==5.0.0']},
    packages=packages,
)
