
from setuptools import setup, find_packages


setup(
    name='modelify',
    version='0.0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='New Version of MLOps Platforms.',
    long_description=" Modelify takes over all devops jobs from data scientists and machine learning practitioners and brings their models to production.",
    install_requires=['numpy',"cloudpickle", 'pyminizip', 'onnxmltools','onnxruntime','skl2onnx','requests-toolbelt','tf2onnx', 'pydantic'],
    author='Muzaffer Senkal',
    author_email='info@modelify.ai',
    keywords=['mlops', 'machine learning', 'model deployment', 'deploy model', 'data science', 'computer vision']
)
