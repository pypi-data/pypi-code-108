from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='PyFLOSIC2',
      version='2.0.0-pre',
      description='Python-based Fermi-Löwdin orbital self-interaction correction (FLO-SIC)',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://gitlab.com/opensic/pyflosic2',
      author='Sebastian Schwalbe',
      author_email='theonov13@gmail.com',
      license='APACHE2.0',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
          'numpy',
          'fodMC',
          'pyscf==1.7.6.post1',
          'ase',
          'distro',
          'scipy',
          'glfw==2.1.0',
          'gr',
          'PyOpenGL==3.1.5',
          'h5py'],
      # Scripts: Ref.:
      # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-scripts-keyword-argument
      scripts=['scripts/pyflosic2'],
      python_requires='>=3.6',
      )
