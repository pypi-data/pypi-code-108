try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='efficientnet_3D',
    version='1.0.2',
    author='Roman Sol (ZFTurbo)',
    packages=['efficientnet_3D', ],
    url='https://github.com/ZFTurbo/efficientnet_3D',
    description='EfficientNet models in 3D variant for keras and TF.keras',
    long_description='EfficientNet models in 3D variant for keras and TF.keras.'
                     'More details: https://github.com/ZFTurbo/efficientnet_3D',
)
