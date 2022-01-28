
from setuptools import setup, find_packages


setup(
    name='modelify',
    version='0.0.1.3',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='New Version of MLOps Platforms.',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    install_requires=['numpy',"cloudpickle", 'pyminizip', 'onnxmltools','onnxruntime','skl2onnx','requests-toolbelt','tf2onnx', 'pydantic'],
    author='Muzaffer Senkal',
    author_email='info@modelify.ai',
    keywords=['mlops', 'machine learning', 'model deployment', 'deploy model', 'data science', 'computer vision']
)
