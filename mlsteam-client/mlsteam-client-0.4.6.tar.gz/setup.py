import os.path
from setuptools import find_packages, setup
# from mlsteam.version import __version__
__version__="0.4.6"

with open(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md"),
    encoding="utf-8",
) as handler:
    long_description = handler.read()


def main():
    root_dir = os.path.dirname(__file__)
    # Get requirements
    requirements = []
    with open(os.path.join(root_dir, 'requirements.txt'), 'r') as infile:
        for line in infile:
            line = line.strip()
            if line and not line[0] == '#':  # ignore comments
                requirements.append(line)
        setup(
            name='mlsteam-client',
            python_requires=">=3.6.0",
            version=__version__,
            description="MLSteam Client",
            author="MyelinTek inc.",
            author_email="simon@myelintek.com",
            url="https://myelintek.com",
            long_description=long_description,
            long_description_content_type="text/markdown",
            license='MIT',
            keywords=['Deep Learning Tracking'],
            packages=find_packages(),
            use_2to3=True,
            include_package_data=True,
            zip_safe=False,
            install_requires=requirements,
            #scripts=['bin/mc'],
            data_files=[('bin', ['bin/mc'])],
            entry_points = {
                'console_scripts':['mlsteam=mlsteam.cli:cli'],
            },
            classifiers=[
                "Development Status :: 3 - Alpha",
                "Environment :: Console",
                "Intended Audience :: Developers",
                "Intended Audience :: Science/Research",
                "License :: OSI Approved :: MIT License",
                "Natural Language :: English",
                "Operating System :: POSIX :: Linux",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Topic :: Software Development :: Libraries :: Python Modules",
                "Programming Language :: Python :: Implementation :: CPython",
                "Topic :: Scientific/Engineering :: Artificial Intelligence"
            ]
        )


if __name__ == "__main__":
    main()
