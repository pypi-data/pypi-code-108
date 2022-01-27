from setuptools import setup

def get_readme():
    try:
        file = open('asklora/README.md')
    except Exception:
        file=open('README.md')
    return file.read()
    

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='asklora-portal',
    url='https://github.com/asklora/asklora-portal.git',
    author='Rede akbar wijaya',
    author_email='asklora@loratechai.com',
    # Needed to actually package something
    packages=['asklora','asklora.Rkd'],
    # Needed for dependencies
    install_requires=['aiohttp','pandas','numpy','requests','cryptography'],
    include_package_data=True,
     package_data={
   'asklora': ['README.md']  #All md files
   },
    # *strongly* suggested for sharing
    version='1.0.4',
    # The license can be anything you like
    license='MIT',
    description='getter price from refinitiv',
    # We will also need a readme eventually (there will be a warning)
    long_description=get_readme(),
    long_description_content_type='text/markdown'
)