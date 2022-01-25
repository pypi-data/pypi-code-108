from setuptools import setup

import os
import sys
import glob
import fnmatch

HERE				= os.path.dirname( os.path.abspath( __file__ ))

def find_data_files( directory, *pats, **kwds ):
    """Using glob patterns in ``package_data`` that matches a directory can result in setuptools trying
    to install that directory as a file and the installation to fail.

    This function walks over the contents of each of the supplied *paths* in *directory* and returns
    a list of only filenames found -- relative to *directory*.

    """
    kwds.setdefault( 'skip', "*~" )
    assert set( kwds ) == { 'skip' }

    def walk( path ):
        for root, dirs, files in os.walk( path ):
            for filename in files:
                yield os.path.join( root, filename )

    strip = os.path.join( HERE, directory )
    result = []
    for pat in pats:
        for path in glob.glob( os.path.join( strip, pat )):
            for filename in walk( path ) if os.path.isdir( path ) else [ path ]:
                if not fnmatch.fnmatch( filename, kwds['skip'] ):
                    result.append( os.path.relpath( filename, strip ))

    return result

# Must work if setup.py is run in the source distribution context, or from
# within the packaged distribution directory.
__version__			= None
try:
    exec( open( 'crypto_licensing/version.py', 'r' ).read() )
except FileNotFoundError:
    exec( open( 'version.py', 'r' ).read() )

console_scripts			= [
    'crypto-licensing		= crypto_licensing.licensing.main:main',
]

entry_points			= {
    'console_scripts': 		console_scripts,
}

install_requires		= open( os.path.join( HERE, "requirements.txt" )).readlines()
tests_require			= open( os.path.join( HERE, "requirements-tests.txt" )).readlines()

package_dir			= {
    "crypto_licensing":			"./crypto_licensing",
    "crypto_licensing/ed25519ll":	"./crypto_licensing/ed25519ll",
    "crypto_licensing/licensing":	"./crypto_licensing/licensing",
}

# Including data in the package is complex: https://sinoroc.gitlab.io/kb/python/package_data.html
# 
# Ship the static data for the crypto_licensing.licensing server, and some demo test data.  From the
# parent of your cpppo source, run:
# 
#     rm -f licensing.* && python3 -m cpppo.crypto.licensing -vv --config cpppo/crypto/licensing/licensing_test --no-gui
# 
package_data			= {
        'crypto_licensing/licensing': find_data_files( 'crypto_licensing/licensing', 'licensing.sql*', 'licensing_test', 'static' )
}

long_description_content_type	= 'text/plain'
long_description		= """\
Licensing software and getting paid for it has become extremely difficult, due to government
regulatory and banking interference.

Using crypto-licensing allows you automatically and securely issue licenses, and get paid in various
cryptocurrencies.
"""

classifiers			= [
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "License :: Other/Proprietary License",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Financial and Insurance Industry",
    "Environment :: Console",
    "Topic :: Security :: Cryptography",
    "Topic :: Office/Business :: Financial",
]
project_urls			= {
    "Bug Tracker": "https://github.com/pjkundert/crypto-licensing/issues",
}
setup(
    name			= "crypto_licensing",
    version			= __version__,
    tests_require		= tests_require,
    install_requires		= install_requires,
    packages			= package_dir.keys(),
    package_dir			= package_dir,
    package_data		= package_data,
    include_package_data	= True,
    zip_safe			= False,
    entry_points		= entry_points,
    author			= "Perry Kundert",
    author_email		= "perry@dominionrnd.com",
    project_urls		= project_urls,
    description			= "The crypto-licensing module implements Ed25519-signed license checking and automatic issuance after cryptocurrency payment",
    long_description		= long_description,
    long_description_content_type = long_description_content_type,
    license			= "Dual License; GPLv3 and Proprietary",
    keywords			= "Licensing Bitcoin Ethereum cryptocurrency Ed25519 signatures",
    url				= "https://github.com/pjkundert/crypto-licensing",
    classifiers			= classifiers,
)
