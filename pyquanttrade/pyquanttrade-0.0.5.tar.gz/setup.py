import setuptools
from setuptools import find_packages
setuptools.setup(
    name="pyquanttrade",  
    version="0.0.5",
    author="Miguel Martin, Marcos Jimenez",
    description="Library for backtesting algorithmic trading strategies using Quandl data",
    
    packages=['pyquanttrade','pyquanttrade.features', 'pyquanttrade.engine', 'pyquanttrade.engine.stats'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
        "datetime",
        "IPython",
        "altair",
        "quandl",
        "python-decouple"
    ],
)
