from setuptools import find_packages, setup

with open("requirements.txt",'r+') as f:
    lines = f.readlines()

requirements = [str(x).strip() for x in lines]

setup(
    version='0.6.0',
    name='rltrade_test',
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=requirements,
    keywords="Reinforcement Learning",
    url="https://github.com/Bonobo791/rl-trade/",
    description="Easy to use Reinforcement Library for finance",
    long_description="rltrade is a library for easily creating Reinforcement Learning Models for finance.",
)