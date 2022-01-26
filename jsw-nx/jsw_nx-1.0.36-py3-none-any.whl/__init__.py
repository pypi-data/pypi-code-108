import pkg_resources

version = pkg_resources.get_distribution('jsw-nx').version
__version__ = version

# next base
from jsw_nx.base.filter import filter
from jsw_nx.base.find import find
from jsw_nx.base.find_index import find_index
from jsw_nx.base.foreach import foreach
from jsw_nx.base.forin import forin
from jsw_nx.base.get import get
from jsw_nx.base.includes import includes
from jsw_nx.base.index import index
from jsw_nx.base.map import map
from jsw_nx.base.mix import mix
from jsw_nx.base.reduce import reduce
from jsw_nx.base.set import set
from jsw_nx.base.type import type

# ruby style
from jsw_nx.rubify.times import times
from jsw_nx.rubify.to_a import to_a
from jsw_nx.rubify.to_b import to_b
from jsw_nx.rubify.to_f import to_f
from jsw_nx.rubify.to_i import to_i
from jsw_nx.rubify.to_n import to_n
from jsw_nx.rubify.to_s import to_s

# next packages
from jsw_nx.packages.days import days
from jsw_nx.packages.param import param
from jsw_nx.packages.qs import qs
from jsw_nx.packages.tmpl import tmpl
from jsw_nx.packages.deep_each import deep_each


# next classes
from jsw_nx.classes.date import Date
from jsw_nx.classes.fileutils import FileUtils as fileutils
from jsw_nx.classes.tar import Tar as tar
from jsw_nx.classes.json import JSON
from jsw_nx.classes.ymd import Ymd
