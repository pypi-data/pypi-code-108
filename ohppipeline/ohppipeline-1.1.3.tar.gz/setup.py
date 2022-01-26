import setuptools as st
import ohppipeline
packages = st.find_packages()
with open("./requirements.txt","r") as f :
    requirements = f.read().splitlines()


st.setup(
        name     = ohppipeline.__name__,
        version  = ohppipeline.__version__,
        setup_requires=[
            "cython"
            ],
        install_requires=requirements,
        packages = packages,
        author   = ohppipeline.__author__,
        package_data = {"ohppipeline.spectral":["data/calibration_tables.dat"]},
        include_package_data=True,
        )
