from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='cicdsample',
    version='1.0.0',
    description='blablabla',
    project_description="It is exactly what you think it is.",
    url='https://github.com/mukkund1996/GithubActions',
    author='Mukkund Sunjii',
    author_email='mukkundsunjii@gmail.com',
    license='MIT',
    zip_safe=False,
    install_requires=[
        "pytest",
    ],
)