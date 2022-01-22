from distutils.core import setup

setup(
    name='xrpy',
    packages=['xrpy'],
    version='0.0.5',
    license='MIT',
    description='Easier XRPL functions',
    author='amiwrpremium',
    author_email='amiwrpremium@gmail.com',
    url='https://github.com/amiwrpremium/xrpy',
    keywords=['xrp', 'xrpl', 'ledger', 'blockchain', 'ripple', 'rippled', 'SDK'],
    install_requires=[
        'xrpl-py',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
