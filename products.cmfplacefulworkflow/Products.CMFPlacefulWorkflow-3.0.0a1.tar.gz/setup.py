from setuptools import setup, find_packages

version = '3.0.0a1'


setup(
    name='Products.CMFPlacefulWorkflow',
    version=version,
    description="Workflow policies for Plone",
    # Note: long_description is in setup.cfg
    # to avoid needing workarounds for UnicodeDecodeErrors.
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords='CMF Plone Zope2 workflow',
    author='Encolpe DEGOUTE',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/Products.CMFPlacefulWorkflow',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.testing',
            'zope.testing',
        ],
    ),
    install_requires=[
        'setuptools',
        'six',
        'zope.component',
        'zope.interface',
        'zope.i18nmessageid',
        'Products.CMFCore',
        'Products.CMFPlone',
        'Products.GenericSetup >= 2.0',
    ],
)
