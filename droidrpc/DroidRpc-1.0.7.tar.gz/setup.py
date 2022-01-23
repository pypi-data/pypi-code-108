from setuptools import setup

def get_readme():
    try:
        file = open('DroidRpc/README.md')
    except Exception:
        file=open('README.md')
    return file.read()
    

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='DroidRpc',
    url='https://github.com/asklora/DROID-V3.git',
    author='Rede akbar - William',
    author_email='asklora@loratechai.com',
    # Needed to actually package something
    packages=['DroidRpc.modules','DroidRpc.client','DroidRpc.converter'],
    # Needed for dependencies
    install_requires=['grpcio','grpcio-tools'],
    include_package_data=True,
     package_data={
   'DroidRpc': ['README.md']  #All md files
   },
    # *strongly* suggested for sharing
    version='1.0.7',
    # The license can be anything you like
    license='MIT',
    description='Droid Rpc for bot functionality',
    # We will also need a readme eventually (there will be a warning)
    long_description=get_readme(),
    long_description_content_type='text/markdown'
)