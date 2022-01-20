import setuptools
package_data={
    'autotk': ['*.pyd', '*.dll'],
}
setuptools.setup(include_package_data=True,packages=setuptools.find_packages("whl"),package_data=package_data,install_requires=[
    'requests>=2.26','Pillow>=8.3','suds-py3>=1.4',"ttkwidgets>=0.12","PyMySQL>=1.0","adb-shell==0.4.0","libusb1>=1.9.3"
])
