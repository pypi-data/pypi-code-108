from setuptools import setup, find_packages

str_version = '1.0.43'

setup(name='mtutils',
      version=str_version,
      description='Commonly used function library by MT',
      url='https://github.com/zywvvd/utils_vvd',
      author='zywvvd',
      author_email='zywvvd@mail.ustc.edu.cn',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      install_requires= ['numba', 'func_timeout', 'pypinyin', 'opencv-python', 'sklearn'],
      python_requires='>=3')