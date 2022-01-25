from setuptools import setup

setup(
name='Interface_KB',
version='0.2.0',
author='Bert Van Acker',
author_email='bert.vanacker@uantwerpen.be',
packages=['Interface_KB'],
url='https://cosysgit.uantwerpen.be/bvanacker/knowledgebase-interface.git',
license='LICENSE.txt',
description='Knowledge-Base (KB) interface (API)',
scripts=['Interface_KB/KB_Interface.py','Interface_KB/ASGFunctions.py','Interface_KB/ContractFunctions.py','Interface_KB/DFAFunctions.py','Interface_KB/HelperFunctions.py','Interface_KB/InterfaceObjects.py','Interface_KB/PerformanceFunctions.py'],
long_description=open('README.md').read(),
install_requires=[
   "pyecore"
],
)
