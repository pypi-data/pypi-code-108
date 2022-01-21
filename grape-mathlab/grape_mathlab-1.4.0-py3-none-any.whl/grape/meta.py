"""Package information"""

def get_current_year():
    """ Return current year """
    from datetime import datetime
    return datetime.now().year

__all__ = [
    '__project__',
    '__title__',
    '__author__',
    '__copyright__',
    '__license__',
    '__version__',
    '__mail__',
    '__maintainer__',
    '__status__',
    '__packagename__']

__project__ = 'GRAPE'
__packagename__ = 'grape-mathlab'
__project__ = 'GRAPE'
__title__ = "grape"
__author__ = "Aurora Maurizio, Martina Teruzzi, Nicola Demo"
__copyright__ = "Copyright 2019-{}, GRAPE contributors".format(get_current_year())
__license__ = "MIT"
__version__ = "1.4.0"
__mail__ = 'auroramaurizio1@gmail.com, teruzzi.martina@gmail.com, demo.nicola@gmail.com'
__maintainer__ = __author__
__status__ = "Alpha"
