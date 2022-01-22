from setuptools import setup, find_packages


setup(
    name='UsefulHelper',
    version='1.7.3',
    author='CleaverCreator',
    author_email='liuhanbo333@icloud.com',
    packages=find_packages(),
    zip_safe=False,
    platforms=['Linux'],
    install_requires=['PyQt5'],
    python_requires='>=3.9',
    description='Some useful tools',
    long_description="""
                    Seeing GitHub
                                    """,
    license='MIT',
    url='https://github.com/CleverCreater/UsefulHelper',
    classifiers=[],
    scripts=['./start.py']
)
